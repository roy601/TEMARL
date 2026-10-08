# TEMARL MARL file structure

Generated: 2026-09-20 01:27:05

Root: `C:\Users\user5\TEMARL\temarl_marl`

Included directories: **10**
Included files: **435**

Excluded: `.git`, `.venv`, `__pycache__`, and `thesis_env`.

## Tree

```text
temarl_marl/
_frozen.py (5,148 bytes)
baselines_marl.py (14,818 bytes)
calibrate_marl.py (4,948 bytes)
DESIGN.md (11,291 bytes)
encoders_marl.py (3,828 bytes)
env_config.json (736 bytes)
env_marl.py (16,523 bytes)
evaluate_marl.py (10,630 bytes)
gates_marl.py (9,280 bytes)
learning_gate_marl.py (7,197 bytes)
mappo.py (19,826 bytes)
prereg_marl.py (8,323 bytes)
pretrain_marl.py (6,688 bytes)
requirements.txt (119 bytes)
results_marl/
  calibration.log (4,520 bytes)
  calibration_grid.json (107,416 bytes)
  gates.json (16,479 bytes)
  gates.log (3,226 bytes)
  learning_gate.json (26,259 bytes)
  learning_gate.log (1,564 bytes)
  loso/
    baselines_loso.json (33,658,818 bytes)
    cells/
      loso_GRU_MAPPO_s0_S1.json (278,183 bytes)
      loso_GRU_MAPPO_s0_S2.json (277,711 bytes)
      loso_GRU_MAPPO_s0_S3.json (277,250 bytes)
      loso_GRU_MAPPO_s0_S4.json (276,871 bytes)
      loso_GRU_MAPPO_s0_S5.json (274,965 bytes)
      loso_GRU_MAPPO_s0_S6.json (276,947 bytes)
      loso_GRU_MAPPO_s0_S7.json (277,086 bytes)
      loso_GRU_MAPPO_s1_S1.json (278,127 bytes)
      loso_GRU_MAPPO_s1_S2.json (277,888 bytes)
      loso_GRU_MAPPO_s1_S3.json (277,283 bytes)
      loso_GRU_MAPPO_s1_S4.json (276,814 bytes)
      loso_GRU_MAPPO_s1_S5.json (274,624 bytes)
      loso_GRU_MAPPO_s1_S6.json (276,830 bytes)
      loso_GRU_MAPPO_s1_S7.json (276,900 bytes)
      loso_GRU_MAPPO_s2_S1.json (278,085 bytes)
      loso_GRU_MAPPO_s2_S2.json (277,725 bytes)
      loso_GRU_MAPPO_s2_S3.json (277,338 bytes)
      loso_GRU_MAPPO_s2_S4.json (276,975 bytes)
      loso_GRU_MAPPO_s2_S5.json (275,057 bytes)
      loso_GRU_MAPPO_s2_S6.json (276,850 bytes)
      loso_GRU_MAPPO_s2_S7.json (277,094 bytes)
      loso_GRU_MAPPO_s3_S1.json (278,137 bytes)
      loso_GRU_MAPPO_s3_S2.json (277,592 bytes)
      loso_GRU_MAPPO_s3_S3.json (277,234 bytes)
      loso_GRU_MAPPO_s3_S4.json (276,447 bytes)
      loso_GRU_MAPPO_s3_S5.json (274,990 bytes)
      loso_GRU_MAPPO_s3_S6.json (276,901 bytes)
      loso_GRU_MAPPO_s3_S7.json (276,899 bytes)
      loso_GRU_MAPPO_s4_S1.json (278,265 bytes)
      loso_GRU_MAPPO_s4_S2.json (277,773 bytes)
      loso_GRU_MAPPO_s4_S3.json (277,221 bytes)
      loso_GRU_MAPPO_s4_S4.json (276,801 bytes)
      loso_GRU_MAPPO_s4_S5.json (274,937 bytes)
      loso_GRU_MAPPO_s4_S6.json (276,935 bytes)
      loso_GRU_MAPPO_s4_S7.json (277,007 bytes)
      loso_NoHistory_MAPPO_s0_S1.json (278,302 bytes)
      loso_NoHistory_MAPPO_s0_S2.json (277,774 bytes)
      loso_NoHistory_MAPPO_s0_S3.json (277,111 bytes)
      loso_NoHistory_MAPPO_s0_S4.json (277,068 bytes)
      loso_NoHistory_MAPPO_s0_S5.json (274,806 bytes)
      loso_NoHistory_MAPPO_s0_S6.json (276,783 bytes)
      loso_NoHistory_MAPPO_s0_S7.json (276,619 bytes)
      loso_NoHistory_MAPPO_s1_S1.json (278,186 bytes)
      loso_NoHistory_MAPPO_s1_S2.json (277,745 bytes)
      loso_NoHistory_MAPPO_s1_S3.json (277,116 bytes)
      loso_NoHistory_MAPPO_s1_S4.json (276,829 bytes)
      loso_NoHistory_MAPPO_s1_S5.json (274,845 bytes)
      loso_NoHistory_MAPPO_s1_S6.json (276,699 bytes)
      loso_NoHistory_MAPPO_s1_S7.json (276,947 bytes)
      loso_NoHistory_MAPPO_s2_S1.json (278,178 bytes)
      loso_NoHistory_MAPPO_s2_S2.json (277,581 bytes)
      loso_NoHistory_MAPPO_s2_S3.json (277,080 bytes)
      loso_NoHistory_MAPPO_s2_S4.json (276,873 bytes)
      loso_NoHistory_MAPPO_s2_S5.json (274,882 bytes)
      loso_NoHistory_MAPPO_s2_S6.json (276,638 bytes)
      loso_NoHistory_MAPPO_s2_S7.json (276,968 bytes)
      loso_NoHistory_MAPPO_s3_S1.json (278,244 bytes)
      loso_NoHistory_MAPPO_s3_S2.json (277,489 bytes)
      loso_NoHistory_MAPPO_s3_S3.json (277,104 bytes)
      loso_NoHistory_MAPPO_s3_S4.json (277,009 bytes)
      loso_NoHistory_MAPPO_s3_S5.json (274,475 bytes)
      loso_NoHistory_MAPPO_s3_S6.json (276,894 bytes)
      loso_NoHistory_MAPPO_s3_S7.json (276,569 bytes)
      loso_NoHistory_MAPPO_s4_S1.json (278,266 bytes)
      loso_NoHistory_MAPPO_s4_S2.json (277,727 bytes)
      loso_NoHistory_MAPPO_s4_S3.json (277,046 bytes)
      loso_NoHistory_MAPPO_s4_S4.json (276,974 bytes)
      loso_NoHistory_MAPPO_s4_S5.json (274,433 bytes)
      loso_NoHistory_MAPPO_s4_S6.json (276,717 bytes)
      loso_NoHistory_MAPPO_s4_S7.json (276,680 bytes)
      loso_SetEncoder_MAPPO_s0_S1.json (278,230 bytes)
      loso_SetEncoder_MAPPO_s0_S2.json (277,803 bytes)
      loso_SetEncoder_MAPPO_s0_S3.json (277,100 bytes)
      loso_SetEncoder_MAPPO_s0_S4.json (277,146 bytes)
      loso_SetEncoder_MAPPO_s0_S5.json (275,018 bytes)
      loso_SetEncoder_MAPPO_s0_S6.json (276,939 bytes)
      loso_SetEncoder_MAPPO_s0_S7.json (277,060 bytes)
      loso_SetEncoder_MAPPO_s1_S1.json (278,136 bytes)
      loso_SetEncoder_MAPPO_s1_S2.json (278,039 bytes)
      loso_SetEncoder_MAPPO_s1_S3.json (277,362 bytes)
      loso_SetEncoder_MAPPO_s1_S4.json (277,094 bytes)
      loso_SetEncoder_MAPPO_s1_S5.json (274,873 bytes)
      loso_SetEncoder_MAPPO_s1_S6.json (276,900 bytes)
      loso_SetEncoder_MAPPO_s1_S7.json (277,213 bytes)
      loso_SetEncoder_MAPPO_s2_S1.json (278,046 bytes)
      loso_SetEncoder_MAPPO_s2_S2.json (277,765 bytes)
      loso_SetEncoder_MAPPO_s2_S3.json (277,324 bytes)
      loso_SetEncoder_MAPPO_s2_S4.json (277,073 bytes)
      loso_SetEncoder_MAPPO_s2_S5.json (274,909 bytes)
      loso_SetEncoder_MAPPO_s2_S6.json (276,851 bytes)
      loso_SetEncoder_MAPPO_s2_S7.json (277,073 bytes)
      loso_SetEncoder_MAPPO_s3_S1.json (278,231 bytes)
      loso_SetEncoder_MAPPO_s3_S2.json (277,715 bytes)
      loso_SetEncoder_MAPPO_s3_S3.json (277,281 bytes)
      loso_SetEncoder_MAPPO_s3_S4.json (276,780 bytes)
      loso_SetEncoder_MAPPO_s3_S5.json (274,981 bytes)
      loso_SetEncoder_MAPPO_s3_S6.json (276,920 bytes)
      loso_SetEncoder_MAPPO_s3_S7.json (277,141 bytes)
      loso_SetEncoder_MAPPO_s4_S1.json (278,407 bytes)
      loso_SetEncoder_MAPPO_s4_S2.json (277,894 bytes)
      loso_SetEncoder_MAPPO_s4_S3.json (277,390 bytes)
      loso_SetEncoder_MAPPO_s4_S4.json (276,856 bytes)
      loso_SetEncoder_MAPPO_s4_S5.json (274,940 bytes)
      loso_SetEncoder_MAPPO_s4_S6.json (276,895 bytes)
      loso_SetEncoder_MAPPO_s4_S7.json (276,794 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S1.json (278,225 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S2.json (278,057 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S3.json (277,243 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S4.json (276,704 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S5.json (274,792 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S6.json (276,956 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S7.json (276,899 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S1.json (278,140 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S2.json (277,831 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S3.json (277,314 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S4.json (276,878 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S5.json (275,035 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S6.json (276,888 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S7.json (277,131 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S1.json (278,110 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S2.json (277,748 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S3.json (277,271 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S4.json (276,855 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S5.json (275,001 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S6.json (276,903 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S7.json (277,122 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S1.json (278,293 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S2.json (277,768 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S3.json (277,293 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S4.json (276,739 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S5.json (274,900 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S6.json (276,900 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S7.json (277,272 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S1.json (278,243 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S2.json (277,802 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S3.json (277,262 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S4.json (277,296 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S5.json (274,792 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S6.json (276,895 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S7.json (276,896 bytes)
    checkpoints/
      loso_GRU_MAPPO_s0_S1.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S2.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S3.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S4.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S5.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S6.pt (416,806 bytes)
      loso_GRU_MAPPO_s0_S7.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S1.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S2.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S3.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S4.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S5.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S6.pt (416,806 bytes)
      loso_GRU_MAPPO_s1_S7.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S1.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S2.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S3.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S4.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S5.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S6.pt (416,806 bytes)
      loso_GRU_MAPPO_s2_S7.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S1.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S2.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S3.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S4.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S5.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S6.pt (416,806 bytes)
      loso_GRU_MAPPO_s3_S7.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S1.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S2.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S3.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S4.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S5.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S6.pt (416,806 bytes)
      loso_GRU_MAPPO_s4_S7.pt (416,806 bytes)
      loso_NoHistory_MAPPO_s0_S1.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S2.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S3.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S4.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S5.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S6.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s0_S7.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S1.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S2.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S3.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S4.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S5.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S6.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s1_S7.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S1.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S2.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S3.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S4.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S5.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S6.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s2_S7.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S1.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S2.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S3.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S4.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S5.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S6.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s3_S7.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S1.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S2.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S3.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S4.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S5.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S6.pt (101,186 bytes)
      loso_NoHistory_MAPPO_s4_S7.pt (101,186 bytes)
      loso_SetEncoder_MAPPO_s0_S1.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S2.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S3.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S4.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S5.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S6.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s0_S7.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S1.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S2.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S3.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S4.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S5.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S6.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s1_S7.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S1.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S2.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S3.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S4.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S5.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S6.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s2_S7.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S1.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S2.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S3.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S4.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S5.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S6.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s3_S7.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S1.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S2.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S3.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S4.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S5.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S6.pt (417,517 bytes)
      loso_SetEncoder_MAPPO_s4_S7.pt (417,517 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S1.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S2.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S3.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S4.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S5.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S6.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s0_S7.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S1.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S2.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S3.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S4.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S5.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S6.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s1_S7.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S1.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S2.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S3.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S4.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S5.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S6.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s2_S7.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S1.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S2.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S3.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S4.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S5.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S6.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s3_S7.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S1.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S2.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S3.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S4.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S5.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S6.pt (426,835 bytes)
      loso_Transformer-RoPE_MAPPO_s4_S7.pt (426,835 bytes)
    RESULT.txt (8,408 bytes)
  main/
  main - Copy.zip (67,263,993 bytes)
  main.zip (67,263,993 bytes)
    baselines_main.json (9,617,949 bytes)
    cells/
      main_GRU_MAPPO_s0.json (277,677 bytes)
      main_GRU_MAPPO_s1.json (277,557 bytes)
      main_GRU_MAPPO_s2.json (277,527 bytes)
      main_GRU_MAPPO_s3.json (277,544 bytes)
      main_GRU_MAPPO_s4.json (277,651 bytes)
      main_GRU_MAPPO_s5.json (277,746 bytes)
      main_GRU_MAPPO_s6.json (277,562 bytes)
      main_GRU_MAPPO_s7.json (277,411 bytes)
      main_GRU_MAPPO_s8.json (277,677 bytes)
      main_GRU_MAPPO_s9.json (277,534 bytes)
      main_LSTM_MAPPO_s0.json (277,664 bytes)
      main_LSTM_MAPPO_s1.json (277,437 bytes)
      main_LSTM_MAPPO_s2.json (277,439 bytes)
      main_LSTM_MAPPO_s3.json (277,673 bytes)
      main_LSTM_MAPPO_s4.json (277,681 bytes)
      main_LSTM_MAPPO_s5.json (277,734 bytes)
      main_LSTM_MAPPO_s6.json (277,699 bytes)
      main_LSTM_MAPPO_s7.json (277,279 bytes)
      main_LSTM_MAPPO_s8.json (277,626 bytes)
      main_LSTM_MAPPO_s9.json (277,482 bytes)
      main_NoHistory_MAPPO_s0.json (277,421 bytes)
      main_NoHistory_MAPPO_s1.json (277,196 bytes)
      main_NoHistory_MAPPO_s2.json (277,159 bytes)
      main_NoHistory_MAPPO_s3.json (277,206 bytes)
      main_NoHistory_MAPPO_s4.json (277,218 bytes)
      main_NoHistory_MAPPO_s5.json (277,447 bytes)
      main_NoHistory_MAPPO_s6.json (277,293 bytes)
      main_NoHistory_MAPPO_s7.json (277,176 bytes)
      main_NoHistory_MAPPO_s8.json (277,238 bytes)
      main_NoHistory_MAPPO_s9.json (277,248 bytes)
      main_SetEncoder_MAPPO_s0.json (277,609 bytes)
      main_SetEncoder_MAPPO_s1.json (277,541 bytes)
      main_SetEncoder_MAPPO_s2.json (277,487 bytes)
      main_SetEncoder_MAPPO_s3.json (277,644 bytes)
      main_SetEncoder_MAPPO_s4.json (277,601 bytes)
      main_SetEncoder_MAPPO_s5.json (277,700 bytes)
      main_SetEncoder_MAPPO_s6.json (277,491 bytes)
      main_SetEncoder_MAPPO_s7.json (277,513 bytes)
      main_SetEncoder_MAPPO_s8.json (277,599 bytes)
      main_SetEncoder_MAPPO_s9.json (277,584 bytes)
      main_Transformer-RoPE_IPPO_s0.json (277,433 bytes)
      main_Transformer-RoPE_IPPO_s1.json (277,390 bytes)
      main_Transformer-RoPE_IPPO_s2.json (277,478 bytes)
      main_Transformer-RoPE_IPPO_s3.json (277,378 bytes)
      main_Transformer-RoPE_IPPO_s4.json (277,535 bytes)
      main_Transformer-RoPE_IPPO_s5.json (277,863 bytes)
      main_Transformer-RoPE_IPPO_s6.json (277,349 bytes)
      main_Transformer-RoPE_IPPO_s7.json (277,335 bytes)
      main_Transformer-RoPE_IPPO_s8.json (277,742 bytes)
      main_Transformer-RoPE_IPPO_s9.json (277,445 bytes)
      main_Transformer-RoPE_MAPPO_s0.json (277,352 bytes)
      main_Transformer-RoPE_MAPPO_s1.json (277,633 bytes)
      main_Transformer-RoPE_MAPPO_s2.json (277,573 bytes)
      main_Transformer-RoPE_MAPPO_s3.json (277,623 bytes)
      main_Transformer-RoPE_MAPPO_s4.json (277,560 bytes)
      main_Transformer-RoPE_MAPPO_s5.json (277,831 bytes)
      main_Transformer-RoPE_MAPPO_s6.json (277,520 bytes)
      main_Transformer-RoPE_MAPPO_s7.json (277,491 bytes)
      main_Transformer-RoPE_MAPPO_s8.json (277,685 bytes)
      main_Transformer-RoPE_MAPPO_s9.json (277,459 bytes)
    checkpoints/
      main_GRU_MAPPO_s0.pt (416,664 bytes)
      main_GRU_MAPPO_s1.pt (416,664 bytes)
      main_GRU_MAPPO_s2.pt (416,664 bytes)
      main_GRU_MAPPO_s3.pt (416,664 bytes)
      main_GRU_MAPPO_s4.pt (416,664 bytes)
      main_GRU_MAPPO_s5.pt (416,664 bytes)
      main_GRU_MAPPO_s6.pt (416,664 bytes)
      main_GRU_MAPPO_s7.pt (416,664 bytes)
      main_GRU_MAPPO_s8.pt (416,664 bytes)
      main_GRU_MAPPO_s9.pt (416,664 bytes)
      main_LSTM_MAPPO_s0.pt (417,074 bytes)
      main_LSTM_MAPPO_s1.pt (417,074 bytes)
      main_LSTM_MAPPO_s2.pt (417,074 bytes)
      main_LSTM_MAPPO_s3.pt (417,074 bytes)
      main_LSTM_MAPPO_s4.pt (417,074 bytes)
      main_LSTM_MAPPO_s5.pt (417,074 bytes)
      main_LSTM_MAPPO_s6.pt (417,074 bytes)
      main_LSTM_MAPPO_s7.pt (417,074 bytes)
      main_LSTM_MAPPO_s8.pt (417,074 bytes)
      main_LSTM_MAPPO_s9.pt (417,074 bytes)
      main_NoHistory_MAPPO_s0.pt (101,068 bytes)
      main_NoHistory_MAPPO_s1.pt (101,068 bytes)
      main_NoHistory_MAPPO_s2.pt (101,068 bytes)
      main_NoHistory_MAPPO_s3.pt (101,068 bytes)
      main_NoHistory_MAPPO_s4.pt (101,068 bytes)
      main_NoHistory_MAPPO_s5.pt (101,068 bytes)
      main_NoHistory_MAPPO_s6.pt (101,068 bytes)
      main_NoHistory_MAPPO_s7.pt (101,068 bytes)
      main_NoHistory_MAPPO_s8.pt (101,068 bytes)
      main_NoHistory_MAPPO_s9.pt (101,068 bytes)
      main_SetEncoder_MAPPO_s0.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s1.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s2.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s3.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s4.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s5.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s6.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s7.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s8.pt (417,436 bytes)
      main_SetEncoder_MAPPO_s9.pt (417,436 bytes)
      main_Transformer-RoPE_IPPO_s0.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s1.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s2.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s3.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s4.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s5.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s6.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s7.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s8.pt (426,551 bytes)
      main_Transformer-RoPE_IPPO_s9.pt (426,551 bytes)
      main_Transformer-RoPE_MAPPO_s0.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s1.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s2.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s3.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s4.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s5.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s6.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s7.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s8.pt (426,606 bytes)
      main_Transformer-RoPE_MAPPO_s9.pt (426,606 bytes)
    RESULT.txt (10,530 bytes)
  smoke_main/
    baselines_main.json (1,156,673 bytes)
    cells/
      main_GRU_MAPPO_s0.json (34,614 bytes)
      main_NoHistory_MAPPO_s0.json (34,502 bytes)
    checkpoints/
      main_GRU_MAPPO_s0.pt (416,664 bytes)
      main_NoHistory_MAPPO_s0.pt (101,068 bytes)
run_marl.py (10,955 bytes)
RUN_ON_GPU_PC.md (4,511 bytes)
scripts_marl.py (11,585 bytes)
tests_marl.py (11,058 bytes)
```

## Files by path

| Relative path | Bytes |
|---|---:|
| `_frozen.py` | 5,148 |
| `baselines_marl.py` | 14,818 |
| `calibrate_marl.py` | 4,948 |
| `DESIGN.md` | 11,291 |
| `encoders_marl.py` | 3,828 |
| `env_config.json` | 736 |
| `env_marl.py` | 16,523 |
| `evaluate_marl.py` | 10,630 |
| `gates_marl.py` | 9,280 |
| `learning_gate_marl.py` | 7,197 |
| `mappo.py` | 19,826 |
| `prereg_marl.py` | 8,323 |
| `pretrain_marl.py` | 6,688 |
| `requirements.txt` | 119 |
| `results_marl/calibration.log` | 4,520 |
| `results_marl/calibration_grid.json` | 107,416 |
| `results_marl/gates.json` | 16,479 |
| `results_marl/gates.log` | 3,226 |
| `results_marl/learning_gate.json` | 26,259 |
| `results_marl/learning_gate.log` | 1,564 |
| `results_marl/loso/baselines_loso.json` | 33,658,818 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S1.json` | 278,183 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S2.json` | 277,711 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S3.json` | 277,250 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S4.json` | 276,871 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S5.json` | 274,965 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S6.json` | 276,947 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s0_S7.json` | 277,086 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S1.json` | 278,127 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S2.json` | 277,888 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S3.json` | 277,283 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S4.json` | 276,814 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S5.json` | 274,624 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S6.json` | 276,830 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s1_S7.json` | 276,900 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S1.json` | 278,085 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S2.json` | 277,725 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S3.json` | 277,338 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S4.json` | 276,975 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S5.json` | 275,057 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S6.json` | 276,850 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s2_S7.json` | 277,094 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S1.json` | 278,137 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S2.json` | 277,592 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S3.json` | 277,234 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S4.json` | 276,447 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S5.json` | 274,990 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S6.json` | 276,901 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s3_S7.json` | 276,899 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S1.json` | 278,265 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S2.json` | 277,773 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S3.json` | 277,221 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S4.json` | 276,801 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S5.json` | 274,937 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S6.json` | 276,935 |
| `results_marl/loso/cells/loso_GRU_MAPPO_s4_S7.json` | 277,007 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S1.json` | 278,302 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S2.json` | 277,774 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S3.json` | 277,111 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S4.json` | 277,068 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S5.json` | 274,806 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S6.json` | 276,783 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s0_S7.json` | 276,619 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S1.json` | 278,186 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S2.json` | 277,745 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S3.json` | 277,116 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S4.json` | 276,829 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S5.json` | 274,845 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S6.json` | 276,699 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s1_S7.json` | 276,947 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S1.json` | 278,178 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S2.json` | 277,581 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S3.json` | 277,080 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S4.json` | 276,873 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S5.json` | 274,882 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S6.json` | 276,638 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s2_S7.json` | 276,968 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S1.json` | 278,244 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S2.json` | 277,489 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S3.json` | 277,104 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S4.json` | 277,009 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S5.json` | 274,475 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S6.json` | 276,894 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s3_S7.json` | 276,569 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S1.json` | 278,266 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S2.json` | 277,727 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S3.json` | 277,046 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S4.json` | 276,974 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S5.json` | 274,433 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S6.json` | 276,717 |
| `results_marl/loso/cells/loso_NoHistory_MAPPO_s4_S7.json` | 276,680 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S1.json` | 278,230 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S2.json` | 277,803 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S3.json` | 277,100 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S4.json` | 277,146 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S5.json` | 275,018 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S6.json` | 276,939 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s0_S7.json` | 277,060 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S1.json` | 278,136 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S2.json` | 278,039 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S3.json` | 277,362 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S4.json` | 277,094 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S5.json` | 274,873 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S6.json` | 276,900 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s1_S7.json` | 277,213 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S1.json` | 278,046 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S2.json` | 277,765 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S3.json` | 277,324 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S4.json` | 277,073 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S5.json` | 274,909 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S6.json` | 276,851 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s2_S7.json` | 277,073 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S1.json` | 278,231 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S2.json` | 277,715 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S3.json` | 277,281 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S4.json` | 276,780 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S5.json` | 274,981 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S6.json` | 276,920 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s3_S7.json` | 277,141 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S1.json` | 278,407 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S2.json` | 277,894 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S3.json` | 277,390 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S4.json` | 276,856 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S5.json` | 274,940 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S6.json` | 276,895 |
| `results_marl/loso/cells/loso_SetEncoder_MAPPO_s4_S7.json` | 276,794 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S1.json` | 278,225 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S2.json` | 278,057 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S3.json` | 277,243 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S4.json` | 276,704 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S5.json` | 274,792 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S6.json` | 276,956 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s0_S7.json` | 276,899 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S1.json` | 278,140 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S2.json` | 277,831 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S3.json` | 277,314 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S4.json` | 276,878 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S5.json` | 275,035 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S6.json` | 276,888 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s1_S7.json` | 277,131 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S1.json` | 278,110 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S2.json` | 277,748 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S3.json` | 277,271 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S4.json` | 276,855 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S5.json` | 275,001 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S6.json` | 276,903 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s2_S7.json` | 277,122 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S1.json` | 278,293 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S2.json` | 277,768 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S3.json` | 277,293 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S4.json` | 276,739 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S5.json` | 274,900 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S6.json` | 276,900 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s3_S7.json` | 277,272 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S1.json` | 278,243 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S2.json` | 277,802 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S3.json` | 277,262 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S4.json` | 277,296 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S5.json` | 274,792 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S6.json` | 276,895 |
| `results_marl/loso/cells/loso_Transformer-RoPE_MAPPO_s4_S7.json` | 276,896 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S1.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S2.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S3.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S4.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S5.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S6.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s0_S7.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S1.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S2.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S3.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S4.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S5.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S6.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s1_S7.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S1.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S2.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S3.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S4.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S5.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S6.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s2_S7.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S1.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S2.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S3.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S4.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S5.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S6.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s3_S7.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S1.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S2.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S3.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S4.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S5.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S6.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_GRU_MAPPO_s4_S7.pt` | 416,806 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S1.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S2.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S3.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S4.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S5.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S6.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s0_S7.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S1.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S2.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S3.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S4.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S5.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S6.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s1_S7.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S1.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S2.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S3.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S4.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S5.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S6.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s2_S7.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S1.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S2.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S3.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S4.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S5.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S6.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s3_S7.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S1.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S2.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S3.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S4.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S5.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S6.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_NoHistory_MAPPO_s4_S7.pt` | 101,186 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S1.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S2.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S3.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S4.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S5.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S6.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s0_S7.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S1.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S2.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S3.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S4.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S5.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S6.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s1_S7.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S1.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S2.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S3.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S4.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S5.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S6.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s2_S7.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S1.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S2.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S3.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S4.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S5.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S6.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s3_S7.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S1.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S2.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S3.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S4.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S5.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S6.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_SetEncoder_MAPPO_s4_S7.pt` | 417,517 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S1.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S2.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S3.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S4.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S5.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S6.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s0_S7.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S1.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S2.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S3.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S4.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S5.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S6.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s1_S7.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S1.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S2.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S3.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S4.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S5.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S6.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s2_S7.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S1.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S2.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S3.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S4.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S5.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S6.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s3_S7.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S1.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S2.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S3.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S4.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S5.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S6.pt` | 426,835 |
| `results_marl/loso/checkpoints/loso_Transformer-RoPE_MAPPO_s4_S7.pt` | 426,835 |
| `results_marl/loso/RESULT.txt` | 8,408 |
| `results_marl/main - Copy.zip` | 67,263,993 |
| `results_marl/main.zip` | 67,263,993 |
| `results_marl/main/baselines_main.json` | 9,617,949 |
| `results_marl/main/cells/main_GRU_MAPPO_s0.json` | 277,677 |
| `results_marl/main/cells/main_GRU_MAPPO_s1.json` | 277,557 |
| `results_marl/main/cells/main_GRU_MAPPO_s2.json` | 277,527 |
| `results_marl/main/cells/main_GRU_MAPPO_s3.json` | 277,544 |
| `results_marl/main/cells/main_GRU_MAPPO_s4.json` | 277,651 |
| `results_marl/main/cells/main_GRU_MAPPO_s5.json` | 277,746 |
| `results_marl/main/cells/main_GRU_MAPPO_s6.json` | 277,562 |
| `results_marl/main/cells/main_GRU_MAPPO_s7.json` | 277,411 |
| `results_marl/main/cells/main_GRU_MAPPO_s8.json` | 277,677 |
| `results_marl/main/cells/main_GRU_MAPPO_s9.json` | 277,534 |
| `results_marl/main/cells/main_LSTM_MAPPO_s0.json` | 277,664 |
| `results_marl/main/cells/main_LSTM_MAPPO_s1.json` | 277,437 |
| `results_marl/main/cells/main_LSTM_MAPPO_s2.json` | 277,439 |
| `results_marl/main/cells/main_LSTM_MAPPO_s3.json` | 277,673 |
| `results_marl/main/cells/main_LSTM_MAPPO_s4.json` | 277,681 |
| `results_marl/main/cells/main_LSTM_MAPPO_s5.json` | 277,734 |
| `results_marl/main/cells/main_LSTM_MAPPO_s6.json` | 277,699 |
| `results_marl/main/cells/main_LSTM_MAPPO_s7.json` | 277,279 |
| `results_marl/main/cells/main_LSTM_MAPPO_s8.json` | 277,626 |
| `results_marl/main/cells/main_LSTM_MAPPO_s9.json` | 277,482 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s0.json` | 277,421 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s1.json` | 277,196 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s2.json` | 277,159 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s3.json` | 277,206 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s4.json` | 277,218 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s5.json` | 277,447 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s6.json` | 277,293 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s7.json` | 277,176 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s8.json` | 277,238 |
| `results_marl/main/cells/main_NoHistory_MAPPO_s9.json` | 277,248 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s0.json` | 277,609 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s1.json` | 277,541 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s2.json` | 277,487 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s3.json` | 277,644 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s4.json` | 277,601 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s5.json` | 277,700 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s6.json` | 277,491 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s7.json` | 277,513 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s8.json` | 277,599 |
| `results_marl/main/cells/main_SetEncoder_MAPPO_s9.json` | 277,584 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s0.json` | 277,433 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s1.json` | 277,390 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s2.json` | 277,478 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s3.json` | 277,378 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s4.json` | 277,535 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s5.json` | 277,863 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s6.json` | 277,349 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s7.json` | 277,335 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s8.json` | 277,742 |
| `results_marl/main/cells/main_Transformer-RoPE_IPPO_s9.json` | 277,445 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s0.json` | 277,352 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s1.json` | 277,633 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s2.json` | 277,573 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s3.json` | 277,623 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s4.json` | 277,560 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s5.json` | 277,831 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s6.json` | 277,520 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s7.json` | 277,491 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s8.json` | 277,685 |
| `results_marl/main/cells/main_Transformer-RoPE_MAPPO_s9.json` | 277,459 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s0.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s1.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s2.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s3.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s4.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s5.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s6.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s7.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s8.pt` | 416,664 |
| `results_marl/main/checkpoints/main_GRU_MAPPO_s9.pt` | 416,664 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s0.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s1.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s2.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s3.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s4.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s5.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s6.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s7.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s8.pt` | 417,074 |
| `results_marl/main/checkpoints/main_LSTM_MAPPO_s9.pt` | 417,074 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s0.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s1.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s2.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s3.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s4.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s5.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s6.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s7.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s8.pt` | 101,068 |
| `results_marl/main/checkpoints/main_NoHistory_MAPPO_s9.pt` | 101,068 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s0.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s1.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s2.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s3.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s4.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s5.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s6.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s7.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s8.pt` | 417,436 |
| `results_marl/main/checkpoints/main_SetEncoder_MAPPO_s9.pt` | 417,436 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s0.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s1.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s2.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s3.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s4.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s5.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s6.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s7.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s8.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_IPPO_s9.pt` | 426,551 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s0.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s1.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s2.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s3.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s4.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s5.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s6.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s7.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s8.pt` | 426,606 |
| `results_marl/main/checkpoints/main_Transformer-RoPE_MAPPO_s9.pt` | 426,606 |
| `results_marl/main/RESULT.txt` | 10,530 |
| `results_marl/smoke_main/baselines_main.json` | 1,156,673 |
| `results_marl/smoke_main/cells/main_GRU_MAPPO_s0.json` | 34,614 |
| `results_marl/smoke_main/cells/main_NoHistory_MAPPO_s0.json` | 34,502 |
| `results_marl/smoke_main/checkpoints/main_GRU_MAPPO_s0.pt` | 416,664 |
| `results_marl/smoke_main/checkpoints/main_NoHistory_MAPPO_s0.pt` | 101,068 |
| `run_marl.py` | 10,955 |
| `RUN_ON_GPU_PC.md` | 4,511 |
| `scripts_marl.py` | 11,585 |
| `tests_marl.py` | 11,058 |
