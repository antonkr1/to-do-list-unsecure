"""Fait échouer le build si pip-audit a trouvé une CVE de sévérité critique.

Usage : python3 pip_audit_gate.py rapport-pip-audit.json
La sévérité est lue dans la base OSV (champ database_specific.severity des avis GitHub).
"""
import json
import sys
import urllib.request

OSV_URL = "https://api.osv.dev/v1/vulns/"


def severity(vuln_id):
    try:
        with urllib.request.urlopen(OSV_URL + vuln_id, timeout=15) as resp:
            data = json.load(resp)
    except Exception as exc:
        # On échoue "fermé" : sans réponse d'OSV, on ne peut pas garantir l'absence de CVE critique
        raise SystemExit(f"pip-audit gate : impossible de lire la sévérité de {vuln_id} sur OSV ({exc})")
    return (data.get("database_specific") or {}).get("severity")


def main(report_path):
    with open(report_path) as f:
        report = json.load(f)

    critical = []
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            ids = [vuln["id"]] + vuln.get("aliases", [])
            ghsa = [i for i in ids if i.startswith("GHSA-")]
            levels = {severity(i) for i in ghsa or ids}
            cves = [i for i in ids if i.startswith("CVE-")]
            if "CRITICAL" in levels:
                critical.append((dep["name"], dep["version"], cves or ids[:1], vuln["fix_versions"]))

    if not critical:
        print("pip-audit gate : aucune CVE critique, OK")
        return 0
    print("pip-audit gate : ECHEC, CVE critiques détectées")
    for name, version, ids, fixes in critical:
        print(f"  - {name} {version} : {', '.join(ids)} (corrigé en {', '.join(fixes) or '?'})")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
