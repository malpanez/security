#!/bin/bash
# Comprehensive validation script
# Runs all checks: syntax, linting, secrets scanning

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0
PASSED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Comprehensive Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to log results
log_pass() {
    local msg=$1
    echo -e "${GREEN}✓ ${msg}${NC}"
    PASSED=$((PASSED + 1))
    return 0
}

log_warn() {
    local msg=$1
    echo -e "${YELLOW}⚠ ${msg}${NC}"
    WARNINGS=$((WARNINGS + 1))
    return 0
}

log_error() {
    local msg=$1
    echo -e "${RED}✗ ${msg}${NC}"
    ERRORS=$((ERRORS + 1))
    return 0
}

# 1. Ansible Configuration Syntax
echo -e "${BLUE}1. Validating ansible.cfg...${NC}"
if ansible-config dump -c ansible.cfg > /dev/null 2>&1; then
    log_pass "ansible.cfg syntax valid"
else
    log_error "ansible.cfg has syntax errors"
fi

# 2. Playbook Syntax Check
echo -e "\n${BLUE}2. Validating playbook syntax...${NC}"
for playbook in playbooks/*.yml; do
    if [[ -f "$playbook" ]]; then
        if ansible-playbook "$playbook" --syntax-check > /dev/null 2>&1; then
            log_pass "$(basename $playbook) syntax valid"
        else
            log_error "$(basename $playbook) syntax error"
            ansible-playbook "$playbook" --syntax-check
        fi
    fi
done

# 3. YAML Lint
echo -e "\n${BLUE}3. Running yamllint...${NC}"
if command -v yamllint &> /dev/null; then
    if yamllint -c .yamllint.yml . > /tmp/yamllint.log 2>&1; then
        log_pass "yamllint passed"
    else
        log_warn "yamllint found issues"
        cat /tmp/yamllint.log
    fi
else
    log_warn "yamllint not installed (pip install yamllint)"
fi

# 4. Ansible Lint
echo -e "\n${BLUE}4. Running ansible-lint...${NC}"
if command -v ansible-lint &> /dev/null; then
    if ansible-lint --profile production > /tmp/ansible-lint.log 2>&1; then
        log_pass "ansible-lint passed"
    else
        log_warn "ansible-lint found issues"
        cat /tmp/ansible-lint.log
    fi
else
    log_warn "ansible-lint not installed (pip install ansible-lint)"
fi

# 5. Secret Scanning
echo -e "\n${BLUE}5. Scanning for secrets/credentials...${NC}"

# Check for hardcoded passwords
if grep -r -i "password\s*:\s*['\"]" playbooks/ roles/ 2>/dev/null | grep -v "no_log\|example\|CHANGEME"; then
    log_error "Found potential hardcoded passwords!"
else
    log_pass "No hardcoded passwords found"
fi

# Check for API keys
if grep -r -E "api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]" . --exclude-dir={.git,.ansible,molecule} 2>/dev/null; then
    log_error "Found potential API keys!"
else
    log_pass "No API keys found"
fi

# Check for AWS credentials
if grep -r -E "aws_(access_key|secret)" . --exclude-dir={.git,.ansible} 2>/dev/null; then
    log_error "Found potential AWS credentials!"
else
    log_pass "No AWS credentials found"
fi

# Check for private keys
if grep -r "BEGIN.*PRIVATE KEY" . --exclude-dir={.git,.ssh} 2>/dev/null; then
    log_error "Found private keys!"
else
    log_pass "No private keys found"
fi

# 6. Security Best Practices
echo -e "\n${BLUE}6. Checking security best practices...${NC}"

# Check for weak SSH ciphers
if grep -r "arcfour\|3des\|des-cbc" roles/sshd_hardening/ 2>/dev/null; then
    log_error "Weak SSH ciphers found"
else
    log_pass "No weak SSH ciphers"
fi

# Check for PermitRootLogin yes
if grep -r "PermitRootLogin.*yes" roles/sshd_hardening/defaults/ 2>/dev/null; then
    log_error "PermitRootLogin yes found in defaults"
else
    log_pass "PermitRootLogin properly configured"
fi

# Check for no_log on sensitive tasks
if grep -r "password\|secret\|token" roles/ playbooks/ 2>/dev/null | grep -v "no_log: true" | grep -v "#" | grep -v "\.bak" | head -5; then
    log_warn "Found sensitive tasks without no_log (showing first 5)"
else
    log_pass "Sensitive tasks have no_log"
fi

# 7. Variable Naming Convention
echo -e "\n${BLUE}7. Checking variable naming...${NC}"
for role in roles/*/defaults/main.yml; do
    if [[ -f "$role" ]]; then
        role_name=$(basename $(dirname $(dirname "$role")))
        # Check if variables are prefixed with role name
        if grep -E "^[a-z_]+:" "$role" | grep -v "^${role_name}_" | grep -v "^#" > /dev/null 2>&1; then
            log_warn "Variables in $role_name should be prefixed with ${role_name}_"
        else
            log_pass "$role_name variables properly prefixed"
        fi
    fi
done

# 8. Required Files
echo -e "\n${BLUE}8. Checking required files...${NC}"

required_files=(
    "README.md"
    "CONTRIBUTING.md"
    "SECURITY.md"
    "LICENSE"
    "galaxy.yml"
    "ansible.cfg"
    ".ansible-lint"
    ".yamllint.yml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        log_pass "$file exists"
    else
        log_error "$file missing"
    fi
done

# 9. Molecule Tests
echo -e "\n${BLUE}9. Checking molecule tests...${NC}"
for role in roles/*/; do
    role_name=$(basename "$role")
    if [[ -d "${role}molecule/default/" ]]; then
        log_pass "$role_name has molecule tests"
    else
        log_warn "$role_name missing molecule tests"
    fi
done

# 10. Argument Specs
echo -e "\n${BLUE}10. Checking argument_specs.yml...${NC}"
for role in roles/*/; do
    role_name=$(basename "$role")
    if [[ -f "${role}meta/argument_specs.yml" ]]; then
        log_pass "$role_name has argument_specs.yml"
    else
        log_error "$role_name missing argument_specs.yml"
    fi
done

# 11. Documentation
echo -e "\n${BLUE}11. Checking documentation...${NC}"
for role in roles/*/; do
    role_name=$(basename "$role")
    if [[ -f "${role}README.md" ]]; then
        log_pass "$role_name has README.md"
    else
        log_warn "$role_name missing README.md"
    fi
done

# 12. Handler/Task Files
echo -e "\n${BLUE}12. Checking task organization...${NC}"
for role in roles/*/; do
    role_name=$(basename "$role")
    if [[ -f "${role}tasks/main.yml" ]]; then
        log_pass "$role_name has tasks/main.yml"
    else
        log_error "$role_name missing tasks/main.yml"
    fi
done

# 13. Trailing Whitespace
echo -e "\n${BLUE}13. Checking for trailing whitespace...${NC}"
if grep -r " $" playbooks/ roles/ --exclude-dir=molecule | head -5; then
    log_warn "Found trailing whitespace (showing first 5)"
else
    log_pass "No trailing whitespace"
fi

# 14. TODO/FIXME Comments
echo -e "\n${BLUE}14. Checking for TODO/FIXME...${NC}"
if grep -r "TODO\|FIXME" roles/ playbooks/ --exclude-dir=molecule 2>/dev/null | head -5; then
    log_warn "Found TODO/FIXME comments (showing first 5)"
else
    log_pass "No TODO/FIXME comments"
fi

# 15. Version Consistency
echo -e "\n${BLUE}15. Checking version format...${NC}"
if [[ -f galaxy.yml ]]; then
    version=$(grep "^version:" galaxy.yml | awk '{print $2}')
    if echo "$version" | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" > /dev/null; then
        log_pass "Version $version follows semver"
    else
        log_error "Version $version doesn't follow semver"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Errors: $ERRORS${NC}"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL CRITICAL CHECKS PASSED${NC}"
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $WARNINGS warnings should be addressed${NC}"
    fi
    exit 0
else
    echo -e "${RED}✗ $ERRORS CRITICAL ERRORS FOUND${NC}"
    echo -e "${YELLOW}Fix errors before proceeding${NC}"
    exit 1
fi
