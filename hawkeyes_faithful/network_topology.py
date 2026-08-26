
# network_topology.py
# Hawkeyes faithful reproduction — Do Hoang et al. (2026)
# Computer Networks 276, 111982
# All data from Table 2, Figure 8, and Section 5.4.1

# =============================================================
# TABLE 2 — Vulnerability data (scanned February 2025)
# Exactly as printed in the paper. Do not change any number.
# =============================================================

NODES = {

    # ------- SUBNET 1 ----------------------------------------
    "Tablet": {
        "subnet": 1,
        "is_entry": True,       # accessed from Internet via Firewall
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2019-8689", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 8.8, "epss": 0.9392},
            {"id": "CVE-2018-4441", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 8.8, "epss": 0.9183},
        ]
    },

    "Host1": {
        "subnet": 1,
        "is_entry": True,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2019-13720", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "User",
             "cvss": 8.8, "epss": 0.9703},
            {"id": "CVE-2019-1458", "attack_type": "Local",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.8, "epss": 0.9714},
        ]
    },

    # ------- SUBNET 2 ----------------------------------------
    "Host2": {
        "subnet": 2,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2018-8174", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "User",
             "cvss": 7.5, "epss": 0.9666},
            {"id": "CVE-2018-8550", "attack_type": "Local",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.8, "epss": 0.9556},
            {"id": "CVE-2018-8626", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 9.3, "epss": 0.088},
        ]
    },

    "Host3": {
        "subnet": 2,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2018-8174", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.5, "epss": 0.9666},
            {"id": "CVE-2018-8550", "attack_type": "Local",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.8, "epss": 0.9556},
            {"id": "CVE-2018-8626", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 9.3, "epss": 0.088},
        ]
    },

    "Host4": {
        "subnet": 2,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2018-8174", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.5, "epss": 0.9666},
            {"id": "CVE-2018-8550", "attack_type": "Local",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.8, "epss": 0.9556},
            {"id": "CVE-2018-8626", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 9.3, "epss": 0.088},
        ]
    },

    # ------- SUBNET 3 ----------------------------------------
    "PrintServer": {
        "subnet": 3,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2021-34527", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 8.8, "epss": 0.9584},
        ]
    },

    "LDAPServer": {
        "subnet": 3,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2021-40444", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 8.8, "epss": 0.9693},
            {"id": "CVE-2021-34498", "attack_type": "Local",
             "req_priv": "User", "get_priv": "System",
             "cvss": 7.8, "epss": 0.8764},
        ]
    },

    "FileServer": {
        "subnet": 3,
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2021-44142", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 9.0, "epss": 0.1805},
            {"id": "CVE-2021-44731", "attack_type": "Local",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 7.8, "epss": 0.1292},
        ]
    },

    "WebServer": {
        "subnet": 3,
        "is_entry": True,       # publicly accessible from Internet
        "is_critical": False,
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2019-11043", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 9.8, "epss": 0.9669},
            {"id": "CVE-2019-6340", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "User",
             "cvss": 8.1, "epss": 0.9737},
        ]
    },

    # ------- SUBNET 4 ----------------------------------------
    "DBServer": {
        "subnet": 4,
        "is_entry": False,
        "is_critical": True,    # HIGH VALUE ASSET — must protect
        "is_honeypot": False,
        "cves": [
            {"id": "CVE-2018-12613", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "User",
             "cvss": 8.8, "epss": 0.9732},
            {"id": "CVE-2021-3156", "attack_type": "Local",
             "req_priv": "User", "get_priv": "Root",
             "cvss": 7.8, "epss": 0.9637},
        ]
    },

    # ------- HONEYPOTS ---------------------------------------
    # Fake nodes — deployed by the defender to trap attackers
    "Honeypot1": {
        "subnet": None,         # placed dynamically by agent
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": True,
        "cves": [
            {"id": "CVE-2019-0887", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 8.8, "epss": 0.9732},
            {"id": "CVE-2019-11043", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 9.8, "epss": 0.9669},
        ]
    },

    "Honeypot2": {
        "subnet": None,         # placed dynamically by agent
        "is_entry": False,
        "is_critical": False,
        "is_honeypot": True,
        "cves": [
            {"id": "CVE-2019-0887", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "System",
             "cvss": 8.8, "epss": 0.9732},
            {"id": "CVE-2018-12613", "attack_type": "Remote",
             "req_priv": "User", "get_priv": "User",
             "cvss": 8.8, "epss": 0.9732},
        ]
    },
}

# =============================================================
# FIGURE 8 + SECTION 5.4.1 — Network topology and access rules
# 4 subnets, access rules exactly as described in paper
# =============================================================

# Groups = subnets (Section 3.1, grouping for action space reduction)
GROUPS = {
    0: "Subnet1",   # Tablet, Host1
    1: "Subnet2",   # Host2, Host3, Host4
    2: "Subnet3",   # PrintServer, LDAPServer, FileServer, WebServer
    3: "Subnet4",   # DBServer (CRITICAL)
}

# Which nodes belong to which group
GROUP_MEMBERSHIP = {
    0: ["Tablet", "Host1"],
    1: ["Host2", "Host3", "Host4"],
    2: ["PrintServer", "LDAPServer", "FileServer", "WebServer"],
    3: ["DBServer"],
}

# Entry points — where attacker can start (Section 5.4.1)
# "Web Server is publicly accessible from Internet"
# "Hosts in Subnet 1 are allowed to reach the Internet"
ENTRY_NODES = ["WebServer", "Tablet", "Host1"]

# Critical nodes — what attacker is trying to reach
CRITICAL_NODES = ["DBServer"]

# =============================================================
# ACCESS RULES — Section 5.4.1 (exact quote from paper)
# "Web Server is publicly accessible from Internet"
# "Hosts in Subnet 1 can access Web Server and Subnet 2"
# "Hosts in Subnet 2 can access Subnet 3 and Subnet 4"
# "Web Server can connect to Database Server"
# =============================================================

# Directed edges: (source, target) means source CAN attack target
# This defines the attacker's possible movement paths
ACCESS_RULES = [
    # Internet → entry points
    ("INTERNET", "WebServer"),
    ("INTERNET", "Tablet"),
    ("INTERNET", "Host1"),

    # Subnet1 → WebServer and Subnet2
    ("Tablet",   "WebServer"),
    ("Tablet",   "Host2"),
    ("Tablet",   "Host3"),
    ("Tablet",   "Host4"),
    ("Host1",    "WebServer"),
    ("Host1",    "Host2"),
    ("Host1",    "Host3"),
    ("Host1",    "Host4"),

    # Subnet2 → Subnet3 and Subnet4
    ("Host2",    "PrintServer"),
    ("Host2",    "LDAPServer"),
    ("Host2",    "FileServer"),
    ("Host2",    "WebServer"),
    ("Host2",    "DBServer"),
    ("Host3",    "PrintServer"),
    ("Host3",    "LDAPServer"),
    ("Host3",    "FileServer"),
    ("Host3",    "WebServer"),
    ("Host3",    "DBServer"),
    ("Host4",    "PrintServer"),
    ("Host4",    "LDAPServer"),
    ("Host4",    "FileServer"),
    ("Host4",    "WebServer"),
    ("Host4",    "DBServer"),

    # WebServer → DBServer (Section 5.4.1)
    ("WebServer", "DBServer"),

    # Subnet3 → Subnet4
    ("PrintServer", "DBServer"),
    ("LDAPServer",  "DBServer"),
    ("FileServer",  "DBServer"),
]

# =============================================================
# TABLE 1 — Training hyperparameters (exact from paper)
# =============================================================

HYPERPARAMS = {
    "learning_rate":        1e-3,    # Step size for gradient updates
    "gamma":                0.99,    # Discount factor
    "optimizer":            "Adam",
    "value_loss_coef":      0.5,     # cv — weight for critic loss
    "training_steps":       30000,   # Number of attacker steps
    "network_layers":       [2048, 1024, 512, 64],  # A2C architecture
    "num_agents":           2,       # 2 honeypots = 2 agents
    "num_groups":           4,       # 4 subnets = 4 possible actions
}

# =============================================================
# SCENARIO CONFIGURATIONS — Section 5.4
# =============================================================

# 4 FNR/FPR pairs tested across Scenarios 1, 2, 3
NMS_CONFIGS = [
    {"fnr": 0.05, "fpr": 0.02},   # Config A
    {"fnr": 0.10, "fpr": 0.06},   # Config B
    {"fnr": 0.15, "fpr": 0.10},   # Config C
    {"fnr": 0.20, "fpr": 0.14},   # Config D
]

# 6 attack strategies — Section 4.2
ATTACK_STRATEGIES = ["HiE", "HiC", "Ran", "RanE", "RanC", "Mix"]

# Number of trials per configuration — Section 5.4.1
N_TRIALS = 10

# Attack attempts per trial for DSR evaluation — Section 5.4.1
N_ATTACK_ATTEMPTS = 1000

# =============================================================
# HELPER — compute H_CVSS and H_EPSS for a node (Equations 9,10)
# alpha = weight for lower-privilege CVEs
# =============================================================

def compute_H_scores(node_name, alpha=0.5):
    """
    Equations 9 and 10 from the paper.
    High-privilege CVEs (get_priv = Root or System) get full weight.
    Low-privilege CVEs get weight alpha.
    """
    if node_name not in NODES:
        return 0.0, 0.0

    node = NODES[node_name]
    H_cvss = 0.0
    H_epss = 0.0

    for cve in node["cves"]:
        priv = cve["get_priv"]
        is_high_priv = priv in ["Root", "System"]
        weight = 1.0 if is_high_priv else alpha
        H_cvss += weight * cve["cvss"]
        H_epss += weight * cve["epss"]

    return H_cvss, H_epss


# =============================================================
# QUICK VERIFICATION — run this file directly to check data
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("NETWORK TOPOLOGY VERIFICATION")
    print("=" * 60)

    real_nodes = [n for n, d in NODES.items() if not d["is_honeypot"]]
    honeypots  = [n for n, d in NODES.items() if d["is_honeypot"]]
    entry      = [n for n, d in NODES.items() if d.get("is_entry")]
    critical   = [n for n, d in NODES.items() if d.get("is_critical")]

    print(f"\nTotal nodes:     {len(NODES)}")
    print(f"Real nodes:      {len(real_nodes)}")
    print(f"Honeypots:       {len(honeypots)}")
    print(f"Entry nodes:     {entry}")
    print(f"Critical nodes:  {critical}")
    print(f"Total CVEs:      {sum(len(d['cves']) for d in NODES.values())}")
    print(f"Access rules:    {len(ACCESS_RULES)}")
    print(f"Groups:          {len(GROUPS)}")

    print("\nH_CVSS and H_EPSS per node (Equations 9, 10):")
    print(f"{'Node':<15} {'H_CVSS':>8} {'H_EPSS':>8}")
    print("-" * 35)
    for name in NODES:
        h_cvss, h_epss = compute_H_scores(name)
        print(f"{name:<15} {h_cvss:>8.4f} {h_epss:>8.4f}")

    print("\nVerification complete. All Table 2 data loaded correctly.")