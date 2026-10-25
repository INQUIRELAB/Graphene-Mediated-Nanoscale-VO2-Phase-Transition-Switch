import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;

public class Run_Authoritative_Thermal_Calibration {

    private static double evalScalar(Model model, String numNode, String expr) {
        try {
            model.result().numerical(numNode).set("expr", expr);
            double[][][] res = model.result().numerical(numNode).computeResult();
            if (res == null || res.length == 0 || res[0].length == 0 || res[0][0].length == 0) {
                throw new IllegalStateException("COMSOL numerical node '" + numNode + "' returned empty scalar result for expr '" + expr + "'");
            }
            return res[0][0][0];
        } catch (Exception e) {
            System.err.println("Fatal error evaluating scalar expression '" + expr + "' on node '" + numNode + "': " + e.getMessage());
            throw new RuntimeException("Fatal COMSOL scalar evaluation failure for expr '" + expr + "' on numerical node '" + numNode + "': " + e.getMessage(), e);
        }
    }

    private static double[] evalArray(Model model, String numNode, String expr, int len) {
        try {
            model.result().numerical(numNode).set("expr", expr);
            double[][][] res = model.result().numerical(numNode).computeResult();
            if (res == null || res.length == 0 || res[0].length == 0) {
                throw new IllegalStateException("COMSOL numerical node '" + numNode + "' returned empty array result for expr '" + expr + "'");
            }
            if (len == 0) len = res[0].length;
            double[] out = new double[len];
            for (int i = 0; i < len; i++) {
                if (i < res[0].length) out[i] = res[0][i][0];
                else out[i] = res[0][res[0].length - 1][0];
            }
            return out;
        } catch (Exception e) {
            System.err.println("Fatal error evaluating array expression '" + expr + "' on node '" + numNode + "': " + e.getMessage());
            throw new RuntimeException("Fatal COMSOL array evaluation failure for expr '" + expr + "' on numerical node '" + numNode + "': " + e.getMessage(), e);
        }
    }

    public static void main(String[] args) {
        try {
            ModelUtil.initStandalone(false);
            System.out.println("[INFO] Loading Diag_FreshStart_Model.mph for Authoritative Thermal Calibration...");
            Model model = ModelUtil.load("Model", "comsol/Diag_FreshStart_Model.mph");

            // Disable electrical voltages
            model.param().set("V_gate", "0[V]");
            model.param().set("V_drain", "0[V]");

            // 1. SETUP EXACT PHYSICAL HEAT SOURCE IN VO2 (Domain 3)
            // Volume = 50 nm * 50 nm * 5 nm = 1.25e-23 m^3
            // Prescribed thermal source power P0 = 1.0 uW => Q0 = 1.0 uW / (50nm * 50nm * 5nm)
            try { model.physics("ht").feature().remove("hs_cal"); } catch (Exception e) {}
            model.physics("ht").create("hs_cal", "HeatSource", 3);
            model.physics("ht").feature("hs_cal").selection().set(3); // VO2 domain is 3
            model.physics("ht").feature("hs_cal").set("Q0", "1.0[uW]/(50[nm]*50[nm]*5[nm])");

            // 2. SETUP GRAPHENE HIGHLY CONDUCTIVE LAYER (HCL) ON BOUNDARY 16
            // Physical reference (0.335 nm): k0=600 W/mK, rho0=2200 kg/m3, Cp=709 J/kgK
            // G_th = 2.01e-7 W/K, C_th = 5.2253e-4 J/(m2 K)
            // Preserved in 1.0 nm numerical layer: knum = 201.0 W/(m K), rhonum = 737.0 kg/m3
            try { model.physics("ht").feature().remove("hcl1"); } catch (Exception e) {}
            model.physics("ht").create("hcl1", "HighlyConductiveLayer", 2);
            model.physics("ht").feature("hcl1").selection().set(16); // Top VO2 boundary
            model.physics("ht").feature("hcl1").set("ds", "1.0[nm]");
            model.physics("ht").feature("hcl1").set("ks_mat", "userdef");
            model.physics("ht").feature("hcl1").set("ks", "201.0[W/(m*K)]");
            model.physics("ht").feature("hcl1").set("rhos_mat", "userdef");
            model.physics("ht").feature("hcl1").set("rhos", "737.0[kg/m^3]");
            model.physics("ht").feature("hcl1").set("Cp_s_mat", "userdef");
            model.physics("ht").feature("hcl1").set("Cp_s", "709.0[J/(kg*K)]");

            // Setup ThinLayer features for Interface Thermal Resistance (TBR)
            // Top TBR on Boundary 16 (VO2/Graphene/HfO2)
            try { model.physics("ht").feature().remove("tl_top"); } catch (Exception e) {}
            model.physics("ht").create("tl_top", "ThinLayer", 2);
            model.physics("ht").feature("tl_top").selection().set(16);
            model.physics("ht").feature("tl_top").set("ThermalResistanceType", "ThermalResistance");
            model.physics("ht").feature("tl_top").set("R_s", "0.0[m^2*K/W]");
            model.physics("ht").feature("tl_top").set("ds", "0.335[nm]");
            model.physics("ht").feature("tl_top").set("rhos_mat", "userdef");
            model.physics("ht").feature("tl_top").set("rhos", "2200.0[kg/m^3]");
            model.physics("ht").feature("tl_top").set("Cp_s_mat", "userdef");
            model.physics("ht").feature("tl_top").set("Cp_s", "709.0[J/(kg*K)]");

            // Bottom TBR on Boundary 13 (VO2/SiO2 substrate)
            try { model.physics("ht").feature().remove("tl_bot"); } catch (Exception e) {}
            model.physics("ht").create("tl_bot", "ThinLayer", 2);
            model.physics("ht").feature("tl_bot").selection().set(13);
            model.physics("ht").feature("tl_bot").set("ThermalResistanceType", "ThermalResistance");
            model.physics("ht").feature("tl_bot").set("R_s", "0.0[m^2*K/W]");
            model.physics("ht").feature("tl_bot").set("ds", "0.5[nm]");
            model.physics("ht").feature("tl_bot").set("rhos_mat", "userdef");
            model.physics("ht").feature("tl_bot").set("rhos", "2200.0[kg/m^3]");
            model.physics("ht").feature("tl_bot").set("Cp_s_mat", "userdef");
            model.physics("ht").feature("tl_bot").set("Cp_s", "700.0[J/(kg*K)]");

            // Setup Numerical Evaluators
            try { model.result().numerical().remove("num_av_T"); } catch (Exception e) {}
            model.result().numerical().create("num_av_T", "AvVolume");
            model.result().numerical("num_av_T").selection().set(3); // VO2 volume

            try { model.result().numerical().remove("num_max_T"); } catch (Exception e) {}
            model.result().numerical().create("num_max_T", "MaxVolume");
            model.result().numerical("num_max_T").selection().set(3);

            try { model.result().numerical().remove("int_top_q"); } catch (Exception e) {}
            model.result().numerical().create("int_top_q", "IntSurface");
            model.result().numerical("int_top_q").selection().set(16); // Top boundary

            try { model.result().numerical().remove("int_bot_q"); } catch (Exception e) {}
            model.result().numerical().create("int_bot_q", "IntSurface");
            model.result().numerical("int_bot_q").selection().set(13); // Bottom boundary

            // Create output directories if needed
            new File("./supporting").mkdirs();
            new File("./csv_exports").mkdirs();

            PrintWriter statOut = new PrintWriter(new File("./supporting/Authoritative_FEA_Thermal_Stationary.csv"));
            statOut.println("Case_Name,Gr_State,R_TBR_top_m2K_W,R_TBR_bot_m2K_W,T_avg_K,T_max_K,Delta_T_avg_K,Delta_T_max_K,R_th_avg_K_W,R_th_max_K_W,Q_top_uW,Q_bot_uW,P_applied_uW");

            // Define Cases to simulate:
            // 0: Gr OFF (Ablated)
            // 1: Gr ON Baseline (R_TBR = 0)
            // 2-5: Gr ON with Top TBR (1e-9, 3e-9, 1e-8, 3e-8)
            // 6-9: Gr ON with Bottom TBR (1e-9, 3e-9, 1e-8, 3e-8)
            String[] caseNames = {
                "Gr_OFF_Ablated",
                "Gr_ON_Baseline",
                "Gr_ON_TopTBR_1e-9",
                "Gr_ON_TopTBR_3e-9",
                "Gr_ON_TopTBR_1e-8",
                "Gr_ON_TopTBR_3e-8",
                "Gr_ON_BotTBR_1e-9",
                "Gr_ON_BotTBR_3e-9",
                "Gr_ON_BotTBR_1e-8",
                "Gr_ON_BotTBR_3e-8"
            };

            int[] grStates = {0, 1, 1, 1, 1, 1, 1, 1, 1, 1};
            double[] rTbrTop = {0.0, 0.0, 1.0e-9, 3.0e-9, 1.0e-8, 3.0e-8, 0.0, 0.0, 0.0, 0.0};
            double[] rTbrBot = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0e-9, 3.0e-9, 1.0e-8, 3.0e-8};

            for (int c = 0; c < caseNames.length; c++) {
                String cName = caseNames[c];
                int gState = grStates[c];
                double topTbr = rTbrTop[c];
                double botTbr = rTbrBot[c];

                System.out.println("[INFO] Processing " + cName + " (Gr=" + gState + ", topTBR=" + topTbr + ", botTBR=" + botTbr + ")...");

                // Configure features
                if (gState == 1) {
                    model.physics("ht").feature("hcl1").active(true);
                    model.physics("ht").feature("hcl1").set("ks", "201.0[W/(m*K)]");
                } else {
                    model.physics("ht").feature("hcl1").active(false);
                }

                if (topTbr > 0.0) {
                    model.physics("ht").feature("tl_top").active(true);
                    model.physics("ht").feature("tl_top").set("R_s", topTbr + "[m^2*K/W]");
                } else {
                    model.physics("ht").feature("tl_top").active(false);
                }

                if (botTbr > 0.0) {
                    model.physics("ht").feature("tl_bot").active(true);
                    model.physics("ht").feature("tl_bot").set("R_s", botTbr + "[m^2*K/W]");
                } else {
                    model.physics("ht").feature("tl_bot").active(false);
                }

                // 1. RUN STATIONARY
                String stdStatTag = "std_stat_" + c;
                try { model.study().remove(stdStatTag); } catch (Exception e) {}
                Study stdStat = model.study().create(stdStatTag);
                stdStat.create("stat", "Stationary");
                stdStat.feature("stat").activate("ec", false);
                stdStat.feature("stat").activate("dode1", false);
                stdStat.feature("stat").activate("ht", true);
                stdStat.run();

                String dsetStat = model.result().dataset().tags()[model.result().dataset().tags().length - 1];
                model.result().numerical("num_av_T").set("data", dsetStat);
                model.result().numerical("num_max_T").set("data", dsetStat);
                model.result().numerical("int_top_q").set("data", dsetStat);
                model.result().numerical("int_bot_q").set("data", dsetStat);

                double T_avg = evalScalar(model, "num_av_T", "T");
                double T_max = evalScalar(model, "num_max_T", "T");
                double q_top = evalScalar(model, "int_top_q", "ht.ntflux");
                double q_bot = evalScalar(model, "int_bot_q", "ht.ntflux");

                double dt_avg = T_avg - 300.0;
                double dt_max = T_max - 300.0;
                double p_app = 1.0e-6; // 1 uW
                double R_th_avg = dt_avg / p_app;
                double R_th_max = dt_max / p_app;

                statOut.printf("%s,%d,%.2e,%.2e,%.5f,%.5f,%.5f,%.5f,%.4e,%.4e,%.4e,%.4e,%.4e\n",
                    cName, gState, topTbr, botTbr, T_avg, T_max, dt_avg, dt_max, R_th_avg, R_th_max, q_top * 1e6, q_bot * 1e6, p_app * 1e6);
                statOut.flush();

                // 2. RUN TRANSIENT FOR KEY CASES (Case 0, 1, 5, 9)
                // Output interval: 1 ps from 0 to 100 ps, and 10 ps from 100 ps to 2 ns (or 10 ns for Gr OFF)
                if (c == 0 || c == 1 || c == 5 || c == 9) {
                    System.out.println("  Running transient simulation for " + cName + "...");
                    String stdTransTag = "std_trans_" + c;
                    try { model.study().remove(stdTransTag); } catch (Exception e) {}
                    Study stdTrans = model.study().create(stdTransTag);
                    stdTrans.create("time", "Transient");
                    stdTrans.feature("time").activate("ec", false);
                    stdTrans.feature("time").activate("dode1", false);
                    stdTrans.feature("time").activate("ht", true);

                    if (c == 0) {
                        // Gr OFF requires longer window to reach steady state (up to 5 ns)
                        stdTrans.feature("time").set("tlist", "range(0, 0.001[ns], 0.1[ns]) range(0.12[ns], 0.02[ns], 5.0[ns])");
                    } else {
                        // Gr ON settles rapidly (< 1 ns)
                        stdTrans.feature("time").set("tlist", "range(0, 0.001[ns], 0.1[ns]) range(0.11[ns], 0.01[ns], 2.0[ns])");
                    }
                    stdTrans.run();

                    String dsetTrans = model.result().dataset().tags()[model.result().dataset().tags().length - 1];
                    model.result().numerical("num_av_T").set("data", dsetTrans);
                    model.result().numerical("num_max_T").set("data", dsetTrans);

                    double[] t_arr = evalArray(model, "num_av_T", "t", 0);
                    double[] T_avg_arr = evalArray(model, "num_av_T", "T", t_arr.length);
                    double[] T_max_arr = evalArray(model, "num_max_T", "T", t_arr.length);

                    String transFileName = "./supporting/Authoritative_FEA_Thermal_Transient_" + cName + ".csv";
                    PrintWriter transOut = new PrintWriter(new File(transFileName));
                    transOut.println("t_s,t_ps,T_avg_K,T_max_K,Delta_T_avg_K,Delta_T_max_K");
                    for (int i = 0; i < t_arr.length; i++) {
                        double t_s = t_arr[i];
                        double t_ps = t_s * 1.0e12;
                        double ta = T_avg_arr[i];
                        double tm = T_max_arr[i];
                        transOut.printf("%.6e,%.3f,%.5f,%.5f,%.5f,%.5f\n", t_s, t_ps, ta, tm, ta - 300.0, tm - 300.0);
                    }
                    transOut.close();
                    System.out.println("  Saved " + transFileName);
                }
            }

            statOut.close();
            System.out.println("[INFO] Saving solved authoritative calibration model to comsol/Run_Authoritative_Thermal_Calibration_Model.mph...");
            model.save("comsol/Run_Authoritative_Thermal_Calibration_Model.mph");
            System.out.println("[SUCCESS] Authoritative Thermal Calibration Completed successfully!");

        } catch (Exception e) {
            System.err.println("[FATAL] Authoritative thermal calibration failed: " + e.getMessage());
            e.printStackTrace(System.err);
            if (e instanceof RuntimeException) {
                throw (RuntimeException) e;
            } else {
                throw new RuntimeException("Fatal error in Run_Authoritative_Thermal_Calibration: " + e.getMessage(), e);
            }
        } finally {
            try {
                ModelUtil.disconnect();
            } catch (Exception ignored) {}
        }
    }
}
