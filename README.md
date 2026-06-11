# alesha_mart_legal_case

## OSINT Tools

The following open-source OSINT tools are included as git submodules under `tools/`:

| Tool | Description | Path |
|------|-------------|------|
| [Sherlock](https://github.com/sherlock-project/sherlock) | Hunt down social media accounts by username | `tools/sherlock` |
| [Maigret](https://github.com/soxoj/maigret) | Collect a dossier on a person by username | `tools/maigret` |
| [SpiderFoot](https://github.com/smicallef/spiderfoot) | Automated OSINT/attack surface intelligence | `tools/spiderfoot` |
| [Social Analyzer](https://github.com/qeeqbox/social-analyzer) | Analyze and find profiles across 1000+ social networks | `tools/social-analyzer` |
| [theHarvester](https://github.com/laramies/theHarvester) | Gather emails, domains, IPs from public sources | `tools/theHarvester` |

## Setup

```bash
# Clone with all submodules
git clone --recurse-submodules <repo-url>

# Or if already cloned, run:
bash install_tools.sh
```

> **Note:** Python 3.x and pip are required. Run `install_tools.sh` to install all dependencies.