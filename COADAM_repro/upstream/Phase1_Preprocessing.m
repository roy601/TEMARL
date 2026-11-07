%% preprocess_all.m
% CoADAM Phase 1: Dataset Preprocessing
% Purpose: Load, clean, normalize, and extract threat profiles from all
%          three IIoT datasets. Map attack labels to MITRE ATT&CK-aligned
%          taxonomy for CoADAM.
%
% Outputs saved to /Users/ujw/Desktop/CoADAM/data/processed/
%   - cic_iiot_2025_processed.mat    (primary dataset)
%   - wustl_iiot_2021_processed.mat  (cross-domain validation 1)
%   - edge_iiot_processed.mat        (cross-domain validation 2)
%   - threat_profiles.mat            (attack distributions per dataset)
%   - preprocessing_report.txt       (full log)
%
% MITRE ATT&CK Taxonomy for CoADAM:
%   1. Reconnaissance    (TA0043) - scanning, fingerprinting, host discovery
%   2. InitialAccess     (TA0001) - brute force, dictionary attacks, exploits
%   3. Execution         (TA0002) - malware, backdoors, command injection
%   4. LateralMovement   (TA0008) - MITM, spoofing, impersonation
%   5. Impact            (TA0040) - DoS, DDoS, flooding, resource exhaustion
%   6. Benign            - normal traffic

clearvars; clc; close all;

fprintf('CoADAM Phase 1: Dataset Preprocessing\n');
fprintf('======================================\n');
fprintf('Date: %s\n\n', char(datetime('now')));

%% Configuration
paths = struct();
paths.cic_benign = '/Users/ujw/Dataset/CIC-IIoT 2025/benign data';
paths.cic_attack = '/Users/ujw/Dataset/CIC-IIoT 2025/attack data';
paths.wustl = '/Users/ujw/Dataset/wustl_iiot_2021.csv';
paths.edge = '/Users/ujw/Dataset/DNN-EdgeIIoT-dataset.csv';

% Output directories
output_dir = '/Users/ujw/Desktop/CoADAM/data/processed';
if ~exist(output_dir, 'dir'), mkdir(output_dir); end

log_dir = '/Users/ujw/Desktop/CoADAM/phase1_preprocessing';
if ~exist(log_dir, 'dir'), mkdir(log_dir); end

% Open log file
log_file = fullfile(log_dir, 'preprocessing_report.txt');
fid = fopen(log_file, 'w');

    function dual_print(fid, fmt, varargin)
        fprintf(fmt, varargin{:});
        fprintf(fid, fmt, varargin{:});
    end

% Reproducibility
rng(42, 'twister');

% Sampling configuration
CIC_SAMPLE_FRACTION = 0.25;
TRAIN_FRACTION = 0.80;

% MITRE ATT&CK taxonomy
MITRE_CATEGORIES = {'Reconnaissance', 'InitialAccess', 'Execution', ...
                     'LateralMovement', 'Impact', 'Benign'};

%% ================================================================
%% DATASET 1: CIC-IIoT-2025 (Primary)
%% ================================================================
dual_print(fid, '\n========================================\n');
dual_print(fid, 'PROCESSING DATASET 1: CIC-IIoT-2025\n');
dual_print(fid, '========================================\n\n');

% --- Columns to exclude (non-numeric, identifiers, raw labels) ---
exclude_cols = {'device_name', 'device_mac', 'label_full', 'label1', ...
    'label2', 'label3', 'label4', 'timestamp', 'timestamp_start', ...
    'timestamp_end', 'log_data-types', 'network_ips_all', ...
    'network_ips_dst', 'network_ips_src', 'network_macs_all', ...
    'network_macs_dst', 'network_macs_src', 'network_ports_all', ...
    'network_ports_dst', 'network_ports_src', 'network_protocols_all', ...
    'network_protocols_dst', 'network_protocols_src'};

% --- MITRE mapping for CIC-IIoT-2025 label2 categories ---
%   label2 values: bruteforce, ddos, dos, malware, mitm, recon, web
cic_mitre_map = containers.Map();
cic_mitre_map('benign')     = 'Benign';
cic_mitre_map('recon')      = 'Reconnaissance';
cic_mitre_map('bruteforce') = 'InitialAccess';
cic_mitre_map('malware')    = 'Execution';
cic_mitre_map('web')        = 'Execution';
cic_mitre_map('mitm')       = 'LateralMovement';
cic_mitre_map('ddos')       = 'Impact';
cic_mitre_map('dos')        = 'Impact';

% --- Load benign data ---
dual_print(fid, 'Loading benign data...\n');
benign_files = dir(fullfile(paths.cic_benign, '*.csv'));
all_benign = [];

for i = 1:length(benign_files)
    filepath = fullfile(paths.cic_benign, benign_files(i).name);
    fprintf('  [%d/%d] %s ... ', i, length(benign_files), benign_files(i).name);
    
    try
        temp = readtable(filepath, 'VariableNamingRule', 'preserve');
        n = height(temp);
        sample_n = round(n * CIC_SAMPLE_FRACTION);
        idx = randperm(n, sample_n);
        all_benign = [all_benign; temp(idx, :)];
        fprintf('%d -> %d samples\n', n, sample_n);
    catch ME
        fprintf('ERROR: %s\n', ME.message);
    end
end
dual_print(fid, 'Total benign samples: %d\n\n', height(all_benign));

% --- Load attack data ---
dual_print(fid, 'Loading attack data...\n');
attack_files = dir(fullfile(paths.cic_attack, '*.csv'));
all_attack = [];

for i = 1:length(attack_files)
    filepath = fullfile(paths.cic_attack, attack_files(i).name);
    fprintf('  [%d/%d] %s ... ', i, length(attack_files), attack_files(i).name);
    
    try
        temp = readtable(filepath, 'VariableNamingRule', 'preserve');
        n = height(temp);
        sample_n = round(n * CIC_SAMPLE_FRACTION);
        idx = randperm(n, sample_n);
        all_attack = [all_attack; temp(idx, :)];
        fprintf('%d -> %d samples\n', n, sample_n);
    catch ME
        fprintf('ERROR: %s\n', ME.message);
    end
end
dual_print(fid, 'Total attack samples: %d\n\n', height(all_attack));

% --- Map to MITRE taxonomy ---
dual_print(fid, 'Mapping to MITRE ATT&CK taxonomy...\n');

% Benign labels
benign_mitre = repmat({'Benign'}, height(all_benign), 1);
benign_label2 = repmat({'benign'}, height(all_benign), 1);
benign_label3 = repmat({'benign'}, height(all_benign), 1);

% Attack labels
attack_label2 = all_attack.label2;
attack_label3 = all_attack.label3;
if ~iscell(attack_label2), attack_label2 = cellstr(attack_label2); end
if ~iscell(attack_label3), attack_label3 = cellstr(attack_label3); end

attack_mitre = cell(height(all_attack), 1);
unmapped_count = 0;
for i = 1:height(all_attack)
    key = lower(strtrim(attack_label2{i}));
    if cic_mitre_map.isKey(key)
        attack_mitre{i} = cic_mitre_map(key);
    else
        attack_mitre{i} = 'Execution';  % conservative default for unknown attacks
        unmapped_count = unmapped_count + 1;
    end
end

if unmapped_count > 0
    dual_print(fid, 'WARNING: %d samples had unmapped label2 values\n', unmapped_count);
end

% --- Remove non-numeric columns and combine ---
all_cols = all_benign.Properties.VariableNames;
keep_cols = all_cols(~ismember(all_cols, exclude_cols));

% Filter to numeric columns only
numeric_keep = {};
for i = 1:length(keep_cols)
    if isnumeric(all_benign.(keep_cols{i}))
        numeric_keep{end+1} = keep_cols{i};
    end
end

dual_print(fid, 'Numeric features retained: %d\n', length(numeric_keep));

% Extract numeric features
benign_features = all_benign(:, numeric_keep);
attack_features = all_attack(:, numeric_keep);

% Combine
combined_features = [benign_features; attack_features];
combined_mitre = [benign_mitre; attack_mitre];
combined_label2 = [benign_label2; attack_label2];
combined_label3 = [benign_label3; attack_label3];

dual_print(fid, 'Combined dataset: %d samples x %d features\n', ...
    height(combined_features), width(combined_features));

% --- Handle missing values ---
dual_print(fid, '\nHandling missing values...\n');
feature_matrix = combined_features{:,:};
total_nan = sum(isnan(feature_matrix), 'all');
total_inf = sum(isinf(feature_matrix), 'all');
dual_print(fid, '  NaN values: %d\n', total_nan);
dual_print(fid, '  Inf values: %d\n', total_inf);

% Replace Inf with NaN first, then impute with column median
feature_matrix(isinf(feature_matrix)) = NaN;
for col = 1:size(feature_matrix, 2)
    nan_idx = isnan(feature_matrix(:, col));
    if any(nan_idx)
        med_val = median(feature_matrix(~nan_idx, col), 'omitnan');
        if isnan(med_val), med_val = 0; end
        feature_matrix(nan_idx, col) = med_val;
    end
end

% Verify clean
remaining_nan = sum(isnan(feature_matrix), 'all');
dual_print(fid, '  Remaining NaN after imputation: %d\n', remaining_nan);

% --- Remove zero-variance features ---
feature_std = std(feature_matrix, 0, 1);
zero_var_idx = feature_std < 1e-10;
num_zero_var = sum(zero_var_idx);
dual_print(fid, '  Zero-variance features removed: %d\n', num_zero_var);

if num_zero_var > 0
    removed_names = numeric_keep(zero_var_idx);
    for i = 1:length(removed_names)
        dual_print(fid, '    Removed: %s\n', removed_names{i});
    end
    feature_matrix(:, zero_var_idx) = [];
    numeric_keep(zero_var_idx) = [];
end

% --- Min-Max Normalization to [0, 1] ---
dual_print(fid, '\nNormalizing features (MinMax [0,1])...\n');
feat_min = min(feature_matrix, [], 1);
feat_max = max(feature_matrix, [], 1);
feat_range = feat_max - feat_min;
feat_range(feat_range == 0) = 1;  % prevent division by zero
normalized_matrix = (feature_matrix - feat_min) ./ feat_range;

% Store normalization parameters for transfer
norm_params = struct();
norm_params.feature_names = numeric_keep;
norm_params.feat_min = feat_min;
norm_params.feat_max = feat_max;

% --- Stratified train/test split ---
dual_print(fid, '\nStratified train/test split (%.0f%%/%.0f%%)...\n', ...
    TRAIN_FRACTION*100, (1-TRAIN_FRACTION)*100);

unique_labels = unique(combined_mitre);
train_idx = [];
test_idx = [];

for i = 1:length(unique_labels)
    label_mask = strcmp(combined_mitre, unique_labels{i});
    label_indices = find(label_mask);
    n = length(label_indices);
    n_train = round(n * TRAIN_FRACTION);
    
    perm = randperm(n);
    train_idx = [train_idx; label_indices(perm(1:n_train))];
    test_idx = [test_idx; label_indices(perm(n_train+1:end))];
end

% Build output structures
cic_train = struct();
cic_train.features = normalized_matrix(train_idx, :);
cic_train.mitre_labels = combined_mitre(train_idx);
cic_train.label2 = combined_label2(train_idx);
cic_train.label3 = combined_label3(train_idx);

cic_test = struct();
cic_test.features = normalized_matrix(test_idx, :);
cic_test.mitre_labels = combined_mitre(test_idx);
cic_test.label2 = combined_label2(test_idx);
cic_test.label3 = combined_label3(test_idx);

cic_meta = struct();
cic_meta.feature_names = numeric_keep;
cic_meta.norm_params = norm_params;
cic_meta.mitre_categories = MITRE_CATEGORIES;
cic_meta.total_samples = size(normalized_matrix, 1);
cic_meta.train_samples = length(train_idx);
cic_meta.test_samples = length(test_idx);
cic_meta.num_features = length(numeric_keep);

% Print distribution
dual_print(fid, '\nCIC-IIoT-2025 MITRE Distribution:\n');
dual_print(fid, '  %-20s %8s %8s %8s\n', 'Category', 'Total', 'Train', 'Test');
dual_print(fid, '  %s\n', repmat('-', 1, 50));
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    total = sum(strcmp(combined_mitre, cat));
    train_n = sum(strcmp(cic_train.mitre_labels, cat));
    test_n = sum(strcmp(cic_test.mitre_labels, cat));
    dual_print(fid, '  %-20s %8d %8d %8d\n', cat, total, train_n, test_n);
end
dual_print(fid, '  %-20s %8d %8d %8d\n', 'TOTAL', ...
    length(combined_mitre), length(train_idx), length(test_idx));

% Save
save(fullfile(output_dir, 'cic_iiot_2025_processed.mat'), ...
    'cic_train', 'cic_test', 'cic_meta', '-v7.3');
dual_print(fid, '\nSaved: cic_iiot_2025_processed.mat\n');

% Clear large variables
clear all_benign all_attack combined_features feature_matrix normalized_matrix;
clear benign_features attack_features temp;

%% ================================================================
%% DATASET 2: WUSTL-IIoT-2021
%% ================================================================
dual_print(fid, '\n\n========================================\n');
dual_print(fid, 'PROCESSING DATASET 2: WUSTL-IIoT-2021\n');
dual_print(fid, '========================================\n\n');

% --- MITRE mapping for WUSTL ---
%   Traffic values: normal, DoS, Reconn, Backdoor, CommInj
wustl_mitre_map = containers.Map();
wustl_mitre_map('normal')   = 'Benign';
wustl_mitre_map('dos')      = 'Impact';
wustl_mitre_map('reconn')   = 'Reconnaissance';
wustl_mitre_map('backdoor') = 'Execution';
wustl_mitre_map('comminj')  = 'Execution';

% --- Load full dataset ---
dual_print(fid, 'Loading WUSTL-IIoT-2021...\n');
opts = detectImportOptions(paths.wustl);

% Force all columns to appropriate types
% Columns 1-2 are timestamps (StartTime, LastTime) - read as string
% Columns 3-4 are IP addresses (SrcAddr, DstAddr) - read as string
% Column 48 is Traffic label - read as string
% Column 49 is Target (binary) - read as double
% Everything else is numeric

for i = 1:length(opts.VariableNames)
    name = opts.VariableNames{i};
    if ismember(name, {'StartTime', 'LastTime', 'SrcAddr', 'DstAddr', 'Traffic'})
        opts = setvartype(opts, name, 'char');
    else
        opts = setvartype(opts, name, 'double');
    end
end

wustl_raw = readtable(paths.wustl, opts);
dual_print(fid, 'Raw rows loaded: %d\n', height(wustl_raw));

% --- Clean: remove header row duplicates ---
% The first data row might contain column names as strings
if ismember('Traffic', wustl_raw.Properties.VariableNames)
    bad_rows = strcmp(wustl_raw.Traffic, 'Traffic');
    if any(bad_rows)
        dual_print(fid, 'Removing %d duplicated header rows\n', sum(bad_rows));
        wustl_raw(bad_rows, :) = [];
    end
end

% Also remove rows where SrcAddr equals 'SrcAddr' (header duplicate)
if ismember('SrcAddr', wustl_raw.Properties.VariableNames)
    bad_rows2 = strcmp(wustl_raw.SrcAddr, 'SrcAddr');
    if any(bad_rows2)
        dual_print(fid, 'Removing %d additional header duplicates\n', sum(bad_rows2));
        wustl_raw(bad_rows2, :) = [];
    end
end

dual_print(fid, 'Clean rows: %d\n', height(wustl_raw));

% --- Extract labels and map to MITRE ---
traffic_labels = wustl_raw.Traffic;
if ~iscell(traffic_labels), traffic_labels = cellstr(traffic_labels); end

wustl_mitre = cell(height(wustl_raw), 1);
for i = 1:height(wustl_raw)
    key = lower(strtrim(traffic_labels{i}));
    if wustl_mitre_map.isKey(key)
        wustl_mitre{i} = wustl_mitre_map(key);
    else
        wustl_mitre{i} = 'Benign';  % default unknown to benign
    end
end

% --- Extract numeric features ---
exclude_wustl = {'StartTime', 'LastTime', 'SrcAddr', 'DstAddr', 'Traffic', 'Target'};
all_cols_w = wustl_raw.Properties.VariableNames;
numeric_cols_w = all_cols_w(~ismember(all_cols_w, exclude_wustl));

wustl_features = zeros(height(wustl_raw), length(numeric_cols_w));
for i = 1:length(numeric_cols_w)
    col_data = wustl_raw.(numeric_cols_w{i});
    if isnumeric(col_data)
        wustl_features(:, i) = col_data;
    else
        wustl_features(:, i) = str2double(col_data);
    end
end

% --- Handle missing values ---
total_nan_w = sum(isnan(wustl_features), 'all');
total_inf_w = sum(isinf(wustl_features), 'all');
dual_print(fid, 'NaN values: %d, Inf values: %d\n', total_nan_w, total_inf_w);

wustl_features(isinf(wustl_features)) = NaN;
for col = 1:size(wustl_features, 2)
    nan_idx = isnan(wustl_features(:, col));
    if any(nan_idx)
        med_val = median(wustl_features(~nan_idx, col), 'omitnan');
        if isnan(med_val), med_val = 0; end
        wustl_features(nan_idx, col) = med_val;
    end
end

% --- Remove zero-variance features ---
wustl_std = std(wustl_features, 0, 1);
zero_var_w = wustl_std < 1e-10;
dual_print(fid, 'Zero-variance features removed: %d\n', sum(zero_var_w));
if any(zero_var_w)
    for i = find(zero_var_w)
        dual_print(fid, '  Removed: %s\n', numeric_cols_w{i});
    end
    wustl_features(:, zero_var_w) = [];
    numeric_cols_w(zero_var_w) = [];
end

% --- Normalize ---
dual_print(fid, 'Normalizing (MinMax [0,1])...\n');
w_min = min(wustl_features, [], 1);
w_max = max(wustl_features, [], 1);
w_range = w_max - w_min;
w_range(w_range == 0) = 1;
wustl_normalized = (wustl_features - w_min) ./ w_range;

% --- Stratified train/test split ---
unique_w = unique(wustl_mitre);
train_idx_w = [];
test_idx_w = [];

for i = 1:length(unique_w)
    mask = strcmp(wustl_mitre, unique_w{i});
    indices = find(mask);
    n = length(indices);
    n_train = round(n * TRAIN_FRACTION);
    perm = randperm(n);
    train_idx_w = [train_idx_w; indices(perm(1:n_train))];
    test_idx_w = [test_idx_w; indices(perm(n_train+1:end))];
end

wustl_train = struct();
wustl_train.features = wustl_normalized(train_idx_w, :);
wustl_train.mitre_labels = wustl_mitre(train_idx_w);
wustl_train.traffic_labels = traffic_labels(train_idx_w);

wustl_test = struct();
wustl_test.features = wustl_normalized(test_idx_w, :);
wustl_test.mitre_labels = wustl_mitre(test_idx_w);
wustl_test.traffic_labels = traffic_labels(test_idx_w);

wustl_meta = struct();
wustl_meta.feature_names = numeric_cols_w;
wustl_meta.norm_min = w_min;
wustl_meta.norm_max = w_max;
wustl_meta.total_samples = size(wustl_normalized, 1);
wustl_meta.train_samples = length(train_idx_w);
wustl_meta.test_samples = length(test_idx_w);
wustl_meta.num_features = length(numeric_cols_w);

% Print distribution
dual_print(fid, '\nWUSTL-IIoT-2021 MITRE Distribution:\n');
dual_print(fid, '  %-20s %8s %8s %8s\n', 'Category', 'Total', 'Train', 'Test');
dual_print(fid, '  %s\n', repmat('-', 1, 50));
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    total = sum(strcmp(wustl_mitre, cat));
    train_n = sum(strcmp(wustl_train.mitre_labels, cat));
    test_n = sum(strcmp(wustl_test.mitre_labels, cat));
    dual_print(fid, '  %-20s %8d %8d %8d\n', cat, total, train_n, test_n);
end

save(fullfile(output_dir, 'wustl_iiot_2021_processed.mat'), ...
    'wustl_train', 'wustl_test', 'wustl_meta', '-v7.3');
dual_print(fid, '\nSaved: wustl_iiot_2021_processed.mat\n');

clear wustl_raw wustl_features wustl_normalized;

%% ================================================================
%% DATASET 3: Edge-IIoTset (DNN)
%% ================================================================
dual_print(fid, '\n\n========================================\n');
dual_print(fid, 'PROCESSING DATASET 3: Edge-IIoTset DNN\n');
dual_print(fid, '========================================\n\n');

% --- MITRE mapping for Edge-IIoTset ---
%   Known Attack_type values from the dataset documentation:
%   Normal, DDoS_UDP, DDoS_ICMP, DDoS_TCP, DDoS_HTTP, DoS_UDP,
%   DoS_ICMP, DoS_TCP, DoS_HTTP, Ransomware, XSS, SQL_injection,
%   Password, Uploading, Vulnerability_scanner, Port_Scanning,
%   Backdoor, Fingerprinting, MITM
edge_mitre_map = containers.Map();
edge_mitre_map('normal')               = 'Benign';
edge_mitre_map('ddos_udp')             = 'Impact';
edge_mitre_map('ddos_icmp')            = 'Impact';
edge_mitre_map('ddos_tcp')             = 'Impact';
edge_mitre_map('ddos_http')            = 'Impact';
edge_mitre_map('dos_udp')              = 'Impact';
edge_mitre_map('dos_icmp')             = 'Impact';
edge_mitre_map('dos_tcp')              = 'Impact';
edge_mitre_map('dos_http')             = 'Impact';
edge_mitre_map('ransomware')           = 'Execution';
edge_mitre_map('xss')                  = 'Execution';
edge_mitre_map('sql_injection')        = 'Execution';
edge_mitre_map('uploading')            = 'Execution';
edge_mitre_map('backdoor')             = 'Execution';
edge_mitre_map('password')             = 'InitialAccess';
edge_mitre_map('vulnerability_scanner') = 'Reconnaissance';
edge_mitre_map('port_scanning')        = 'Reconnaissance';
edge_mitre_map('fingerprinting')       = 'Reconnaissance';
edge_mitre_map('mitm')                 = 'LateralMovement';

% --- Load with explicit comma delimiter ---
dual_print(fid, 'Loading Edge-IIoTset DNN (this will take a few minutes)...\n');

% Read header first to get column names
fid_edge = fopen(paths.edge, 'r');
header_line = fgetl(fid_edge);
fclose(fid_edge);
edge_col_names = strsplit(header_line, ',');
num_edge_cols = length(edge_col_names);
dual_print(fid, 'Detected %d columns from header\n', num_edge_cols);

% Set up import options with correct delimiter
opts_edge = delimitedTextImportOptions('NumVariables', num_edge_cols);
opts_edge.Delimiter = ',';
opts_edge.VariableNames = matlab.lang.makeValidName(edge_col_names);
opts_edge.DataLines = [2, Inf];  % skip header row

% Set all columns to char initially to avoid parse errors
for i = 1:num_edge_cols
    opts_edge.VariableTypes{i} = 'char';
end

dual_print(fid, 'Reading file...\n');
tic;
edge_raw = readtable(paths.edge, opts_edge);
read_time = toc;
dual_print(fid, 'Loaded %d rows in %.1f seconds\n', height(edge_raw), read_time);

% --- Identify label columns ---
% Last two columns should be Attack_label and Attack_type
edge_col_list = edge_raw.Properties.VariableNames;
dual_print(fid, 'Last 5 columns: %s\n', strjoin(edge_col_list(end-4:end), ', '));

% Find label columns
attack_label_col = edge_col_list{end-1};  % Attack_label (binary)
attack_type_col = edge_col_list{end};     % Attack_type (specific)

dual_print(fid, 'Attack label column: %s\n', attack_label_col);
dual_print(fid, 'Attack type column: %s\n', attack_type_col);

% Get attack type values
edge_attack_types = edge_raw.(attack_type_col);
if ~iscell(edge_attack_types), edge_attack_types = cellstr(edge_attack_types); end

unique_edge_attacks = unique(edge_attack_types);
dual_print(fid, '\nAttack types found (%d unique):\n', length(unique_edge_attacks));
for i = 1:length(unique_edge_attacks)
    count = sum(strcmp(edge_attack_types, unique_edge_attacks{i}));
    dual_print(fid, '  %-30s %8d (%.2f%%)\n', unique_edge_attacks{i}, count, ...
        100*count/length(edge_attack_types));
end

% --- Map to MITRE ---
edge_mitre = cell(height(edge_raw), 1);
unmapped_edge = 0;
for i = 1:height(edge_raw)
    key = lower(strtrim(edge_attack_types{i}));
    if edge_mitre_map.isKey(key)
        edge_mitre{i} = edge_mitre_map(key);
    else
        edge_mitre{i} = 'Execution';  % conservative default
        unmapped_edge = unmapped_edge + 1;
    end
end
if unmapped_edge > 0
    dual_print(fid, 'Unmapped attack types: %d samples\n', unmapped_edge);
end

% --- Convert numeric columns ---
dual_print(fid, '\nConverting to numeric features...\n');

% Exclude first column (timestamp), last two (labels), and known string columns
exclude_edge = {edge_col_list{1}, attack_label_col, attack_type_col};

% Also exclude known string columns
string_cols_edge = {};
for i = 1:length(edge_col_list)
    if ismember(edge_col_list{i}, exclude_edge)
        continue;
    end
    col_data = edge_raw.(edge_col_list{i});
    if iscell(col_data)
        sample = col_data(1:min(100, end));
        numeric_test = str2double(sample);
        if sum(isnan(numeric_test)) > 50  % more than half failed to convert
            string_cols_edge{end+1} = edge_col_list{i};
        end
    end
end

if ~isempty(string_cols_edge)
    dual_print(fid, 'Non-numeric columns excluded: %s\n', strjoin(string_cols_edge, ', '));
    exclude_edge = [exclude_edge, string_cols_edge];
end

numeric_cols_edge = edge_col_list(~ismember(edge_col_list, exclude_edge));
dual_print(fid, 'Numeric feature columns: %d\n', length(numeric_cols_edge));

% Convert to numeric matrix
edge_features = zeros(height(edge_raw), length(numeric_cols_edge));
for i = 1:length(numeric_cols_edge)
    col_data = edge_raw.(numeric_cols_edge{i});
    if iscell(col_data) || isstring(col_data)
        edge_features(:, i) = str2double(col_data);
    elseif isnumeric(col_data)
        edge_features(:, i) = col_data;
    else
        edge_features(:, i) = str2double(string(col_data));
    end
    
    if mod(i, 10) == 0
        fprintf('  Converted %d/%d columns\n', i, length(numeric_cols_edge));
    end
end

% --- Handle missing values ---
total_nan_e = sum(isnan(edge_features), 'all');
total_inf_e = sum(isinf(edge_features), 'all');
dual_print(fid, 'NaN values: %d, Inf values: %d\n', total_nan_e, total_inf_e);

edge_features(isinf(edge_features)) = NaN;
for col = 1:size(edge_features, 2)
    nan_idx = isnan(edge_features(:, col));
    if any(nan_idx)
        med_val = median(edge_features(~nan_idx, col), 'omitnan');
        if isnan(med_val), med_val = 0; end
        edge_features(nan_idx, col) = med_val;
    end
end

% --- Remove zero-variance ---
edge_std = std(edge_features, 0, 1);
zero_var_e = edge_std < 1e-10;
dual_print(fid, 'Zero-variance features removed: %d\n', sum(zero_var_e));
if any(zero_var_e)
    edge_features(:, zero_var_e) = [];
    numeric_cols_edge(zero_var_e) = [];
end

% --- Normalize ---
dual_print(fid, 'Normalizing (MinMax [0,1])...\n');
e_min = min(edge_features, [], 1);
e_max = max(edge_features, [], 1);
e_range = e_max - e_min;
e_range(e_range == 0) = 1;
edge_normalized = (edge_features - e_min) ./ e_range;

% --- Stratified train/test split ---
unique_e = unique(edge_mitre);
train_idx_e = [];
test_idx_e = [];

for i = 1:length(unique_e)
    mask = strcmp(edge_mitre, unique_e{i});
    indices = find(mask);
    n = length(indices);
    n_train = round(n * TRAIN_FRACTION);
    perm = randperm(n);
    train_idx_e = [train_idx_e; indices(perm(1:n_train))];
    test_idx_e = [test_idx_e; indices(perm(n_train+1:end))];
end

edge_train = struct();
edge_train.features = edge_normalized(train_idx_e, :);
edge_train.mitre_labels = edge_mitre(train_idx_e);
edge_train.attack_types = edge_attack_types(train_idx_e);

edge_test = struct();
edge_test.features = edge_normalized(test_idx_e, :);
edge_test.mitre_labels = edge_mitre(test_idx_e);
edge_test.attack_types = edge_attack_types(test_idx_e);

edge_meta = struct();
edge_meta.feature_names = numeric_cols_edge;
edge_meta.norm_min = e_min;
edge_meta.norm_max = e_max;
edge_meta.total_samples = size(edge_normalized, 1);
edge_meta.train_samples = length(train_idx_e);
edge_meta.test_samples = length(test_idx_e);
edge_meta.num_features = length(numeric_cols_edge);

% Print distribution
dual_print(fid, '\nEdge-IIoTset MITRE Distribution:\n');
dual_print(fid, '  %-20s %8s %8s %8s\n', 'Category', 'Total', 'Train', 'Test');
dual_print(fid, '  %s\n', repmat('-', 1, 50));
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    total = sum(strcmp(edge_mitre, cat));
    train_n = sum(strcmp(edge_train.mitre_labels, cat));
    test_n = sum(strcmp(edge_test.mitre_labels, cat));
    dual_print(fid, '  %-20s %8d %8d %8d\n', cat, total, train_n, test_n);
end

save(fullfile(output_dir, 'edge_iiot_processed.mat'), ...
    'edge_train', 'edge_test', 'edge_meta', '-v7.3');
dual_print(fid, '\nSaved: edge_iiot_processed.mat\n');

clear edge_raw edge_features edge_normalized;

%% ================================================================
%% THREAT PROFILES (Attack distributions for environment simulation)
%% ================================================================
dual_print(fid, '\n\n========================================\n');
dual_print(fid, 'GENERATING THREAT PROFILES\n');
dual_print(fid, '========================================\n\n');

threat_profiles = struct();

% CIC-IIoT-2025 profile
threat_profiles.cic = struct();
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    threat_profiles.cic.(cat) = sum(strcmp(cic_train.mitre_labels, cat)) / length(cic_train.mitre_labels);
end

% WUSTL profile
threat_profiles.wustl = struct();
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    threat_profiles.wustl.(cat) = sum(strcmp(wustl_train.mitre_labels, cat)) / length(wustl_train.mitre_labels);
end

% Edge profile
threat_profiles.edge = struct();
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    threat_profiles.edge.(cat) = sum(strcmp(edge_train.mitre_labels, cat)) / length(edge_train.mitre_labels);
end

% Print comparison
dual_print(fid, 'Threat Profile Comparison (attack proportions):\n');
dual_print(fid, '  %-20s %10s %10s %10s\n', 'Category', 'CIC-IIoT', 'WUSTL', 'Edge');
dual_print(fid, '  %s\n', repmat('-', 1, 55));
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    dual_print(fid, '  %-20s %9.2f%% %9.2f%% %9.2f%%\n', cat, ...
        threat_profiles.cic.(cat)*100, ...
        threat_profiles.wustl.(cat)*100, ...
        threat_profiles.edge.(cat)*100);
end

% MITRE ATT&CK technique mapping reference (for the paper)
mitre_reference = struct();
mitre_reference.Reconnaissance = struct('tactic_id', 'TA0043', ...
    'techniques', {{'T1595-Active Scanning', 'T1592-Gather Host Info', 'T1590-Network Scanning'}}, ...
    'cic_labels', {{'recon'}}, ...
    'wustl_labels', {{'Reconn'}}, ...
    'edge_labels', {{'Vulnerability_scanner', 'Port_Scanning', 'Fingerprinting'}});

mitre_reference.InitialAccess = struct('tactic_id', 'TA0001', ...
    'techniques', {{'T1110-Brute Force', 'T1078-Valid Accounts', 'T1190-Exploit Public App'}}, ...
    'cic_labels', {{'bruteforce'}}, ...
    'wustl_labels', {{}}, ...
    'edge_labels', {{'Password'}});

mitre_reference.Execution = struct('tactic_id', 'TA0002', ...
    'techniques', {{'T1059-Command Scripting', 'T1203-Exploitation', 'T1569-System Services'}}, ...
    'cic_labels', {{'malware', 'web'}}, ...
    'wustl_labels', {{'Backdoor', 'CommInj'}}, ...
    'edge_labels', {{'Ransomware', 'XSS', 'SQL_injection', 'Uploading', 'Backdoor'}});

mitre_reference.LateralMovement = struct('tactic_id', 'TA0008', ...
    'techniques', {{'T1557-Adversary-in-the-Middle', 'T1021-Remote Services'}}, ...
    'cic_labels', {{'mitm'}}, ...
    'wustl_labels', {{}}, ...
    'edge_labels', {{'MITM'}});

mitre_reference.Impact = struct('tactic_id', 'TA0040', ...
    'techniques', {{'T1498-Network DoS', 'T1499-Endpoint DoS', 'T1489-Service Stop'}}, ...
    'cic_labels', {{'ddos', 'dos'}}, ...
    'wustl_labels', {{'DoS'}}, ...
    'edge_labels', {{'DDoS_UDP', 'DDoS_ICMP', 'DDoS_TCP', 'DDoS_HTTP', ...
                     'DoS_UDP', 'DoS_ICMP', 'DoS_TCP', 'DoS_HTTP'}});

threat_profiles.mitre_reference = mitre_reference;

save(fullfile(output_dir, 'threat_profiles.mat'), 'threat_profiles', '-v7.3');
dual_print(fid, '\nSaved: threat_profiles.mat\n');

%% ================================================================
%% FINAL SUMMARY
%% ================================================================
dual_print(fid, '\n\n========================================\n');
dual_print(fid, 'PREPROCESSING COMPLETE\n');
dual_print(fid, '========================================\n\n');

dual_print(fid, 'Output files in %s:\n', output_dir);
dual_print(fid, '  1. cic_iiot_2025_processed.mat\n');
dual_print(fid, '     Train: %d samples, Test: %d samples, Features: %d\n', ...
    cic_meta.train_samples, cic_meta.test_samples, cic_meta.num_features);
dual_print(fid, '  2. wustl_iiot_2021_processed.mat\n');
dual_print(fid, '     Train: %d samples, Test: %d samples, Features: %d\n', ...
    wustl_meta.train_samples, wustl_meta.test_samples, wustl_meta.num_features);
dual_print(fid, '  3. edge_iiot_processed.mat\n');
dual_print(fid, '     Train: %d samples, Test: %d samples, Features: %d\n', ...
    edge_meta.train_samples, edge_meta.test_samples, edge_meta.num_features);
dual_print(fid, '  4. threat_profiles.mat\n');
dual_print(fid, '     MITRE-aligned attack distributions for all 3 datasets\n');

dual_print(fid, '\nMITRE ATT&CK Taxonomy:\n');
for i = 1:length(MITRE_CATEGORIES)
    cat = MITRE_CATEGORIES{i};
    if isfield(mitre_reference, cat)
        dual_print(fid, '  %s (%s)\n', cat, mitre_reference.(cat).tactic_id);
    else
        dual_print(fid, '  %s\n', cat);
    end
end

dual_print(fid, '\nPreprocessing completed: %s\n', char(datetime('now')));

fclose(fid);

fprintf('\n--- Phase 1 complete ---\n');
fprintf('Report: %s\n', log_file);
fprintf('Data: %s\n', output_dir);
fprintf('Share the preprocessing_report.txt output with me.\n');
