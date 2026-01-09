#!/bin/bash
# Kickstart Script - malpanez.security TOP 0.01% Implementation
# This script helps you start the implementation journey

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   malpanez.security - TOP 0.01% Implementation Plan      ║
║                                                           ║
║   From 7.5/10 → 9.8/10                                   ║
║   Duration: 12-14 weeks                                   ║
║   Budget: $50k-$120k                                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}🚀 Welcome to the implementation kickstart!${NC}"
echo ""

# Check if already on a feature branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "feature/top-0.01-percent" ]]; then
    echo -e "${GREEN}✅ Already on feature branch: $current_branch${NC}"
else
    echo -e "${YELLOW}📋 Current branch: $current_branch${NC}"
    echo ""
read -r -p "Create feature branch 'feature/top-0.01-percent'? (y/n) " -n 1
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout -b feature/top-0.01-percent
        echo -e "${GREEN}✅ Created and switched to feature/top-0.01-percent${NC}"
    else
        echo -e "${YELLOW}⚠️  Continuing on current branch${NC}"
    fi
fi

echo ""
echo -e "${CYAN}📚 Available Documentation:${NC}"
echo -e "  1. ${GREEN}START_HERE.md${NC}             - Comprehensive implementation guide"
echo -e "  2. ${GREEN}EXECUTIVE_SUMMARY.md${NC}      - Business case for stakeholders"
echo -e "  3. ${GREEN}IMPLEMENTATION_CHECKLIST.md${NC} - Day-by-day tasks (78 days)"
echo -e "  4. ${GREEN}IMPLEMENTATION_PROMPT.md${NC}  - LLM prompts with technical specs"
echo -e "  5. ${GREEN}QUICK_REFERENCE.md${NC}        - Commands and troubleshooting"

echo ""
read -r -p "Open START_HERE.md now? (y/n) " -n 1
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v code &> /dev/null; then
        code START_HERE.md
        echo -e "${GREEN}✅ Opened in VS Code${NC}"
    elif command -v vim &> /dev/null; then
        vim START_HERE.md
    else
        cat START_HERE.md
    fi
fi

echo ""
echo -e "${CYAN}🔍 Pre-flight Checks:${NC}"
echo ""

# Check 1: Dependencies
echo -n "Checking dependencies... "
missing_deps=()

command -v ansible &> /dev/null || missing_deps+=("ansible-core")
command -v molecule &> /dev/null || missing_deps+=("molecule")
command -v docker &> /dev/null || missing_deps+=("docker")
command -v pytest &> /dev/null || missing_deps+=("pytest")

if [[ ${#missing_deps[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ All dependencies installed${NC}"
else
    echo -e "${RED}❌ Missing dependencies:${NC}"
    for dep in "${missing_deps[@]}"; do
        echo -e "   ${RED}- $dep${NC}"
    done
    echo ""
    echo -e "${YELLOW}Install with:${NC}"
    echo "  pip install ansible-core molecule molecule-docker pytest hypothesis"
    echo "  # Install Docker from https://docs.docker.com/get-docker/"
fi

echo ""

# Check 2: Git status
echo -n "Checking git status... "
if git diff --quiet && git diff --staged --quiet; then
    echo -e "${GREEN}✅ Working directory clean${NC}"
else
    echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
    echo -e "   ${YELLOW}Commit or stash changes before proceeding${NC}"
fi

echo ""

# Check 3: Validation baseline
echo -n "Running validation baseline... "
baseline_log=$(mktemp -t validate-baseline.XXXXXX)
trap 'rm -f "$baseline_log"' EXIT
if ./scripts/validate-all.sh &> "$baseline_log"; then
    echo -e "${GREEN}✅ Baseline validation passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some validations failed (see ${baseline_log})${NC}"
    echo -e "   ${YELLOW}This is expected - we'll fix these issues during implementation${NC}"
fi

echo ""

# Check 4: Docker running
echo -n "Checking Docker... "
if docker ps &> /dev/null; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running${NC}"
    echo -e "   ${YELLOW}Start Docker before running tests${NC}"
fi

echo ""
echo -e "${CYAN}📊 Current Status:${NC}"
echo ""
echo -e "  Score:        ${YELLOW}7.5/10${NC} → ${GREEN}9.8/10${NC} (Target)"
echo -e "  Tasks:        ${YELLOW}0/300+${NC} completed"
echo -e "  Timeline:     ${YELLOW}Day 0/78${NC}"
echo -e "  Phase:        ${YELLOW}Planning${NC}"
echo ""

echo -e "${CYAN}🎯 Next Steps:${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} Read START_HERE.md for strategies"
echo -e "  ${GREEN}2.${NC} Review IMPLEMENTATION_CHECKLIST.md"
echo -e "  ${GREEN}3.${NC} If stakeholder approval needed, share EXECUTIVE_SUMMARY.md"
echo -e "  ${GREEN}4.${NC} When ready, start with Day 1 tasks:"
echo ""
echo -e "     ${CYAN}# Create first test${NC}"
echo -e "     mkdir -p molecule/complete_stack"
echo -e "     # Use LLM to generate test files (see IMPLEMENTATION_PROMPT.md)"
echo ""
echo -e "  ${GREEN}5.${NC} Track progress in IMPLEMENTATION_CHECKLIST.md"
echo ""

echo -e "${CYAN}💡 Quick Commands:${NC}"
echo ""
echo -e "  ${CYAN}# View checklist${NC}"
echo -e "  code IMPLEMENTATION_CHECKLIST.md"
echo ""
echo -e "  ${CYAN}# Run validation${NC}"
echo -e "  ./scripts/validate-all.sh"
echo ""
echo -e "  ${CYAN}# Quick win: Fix no_log violations${NC}"
echo -e "  python scripts/validate-no-log.py  # (Need to create first)"
echo ""
echo -e "  ${CYAN}# Start first test${NC}"
echo -e "  molecule init scenario complete_stack --driver-name docker"
echo ""

echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}   🚀 Ready to start the journey to TOP 0.01%!${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Create journey log
if [[ ! -f JOURNEY_LOG.md ]]; then
    cat > JOURNEY_LOG.md << EOF
# Journey to TOP 0.01% - Log

**Started**: $(date)
**Branch**: $(git branch --show-current)
**Initial Score**: 7.5/10
**Target Score**: 9.8/10

## Progress Log

### Week 0 - Planning
- $(date +'%Y-%m-%d'): Kickstart script executed
- Review documentation
- Setup environment

### Week 1 - Testing Infrastructure
...

EOF
    echo -e "${GREEN}✅ Created JOURNEY_LOG.md to track your progress${NC}"
    echo ""
fi

echo -e "${CYAN}Track your progress in JOURNEY_LOG.md${NC}"
echo ""
echo -e "${YELLOW}Good luck! 💪${NC}"
echo ""
