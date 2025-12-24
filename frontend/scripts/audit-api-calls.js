#!/usr/bin/env node
/**
 * API Call Audit Script
 * 
 * This script scans your React codebase for common patterns that cause
 * duplicate API calls and provides actionable fixes.
 * 
 * Usage:
 *   node audit-api-calls.js
 * 
 * Or add to package.json:
 *   "scripts": {
 *     "audit:api": "node scripts/audit-api-calls.js"
 *   }
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  searchDir: '../frontend/app',
  fileExtensions: ['.tsx', '.ts', '.jsx', '.js'],
  excludeDirs: ['node_modules', '.next', 'dist', 'build'],
};

// Problematic patterns
const PATTERNS = {
  // useEffect with function dependencies
  functionDeps: {
    regex: /useEffect\s*\(\s*(?:async\s*)?\(\s*\)\s*=>\s*\{[\s\S]*?\},\s*\[[\s\S]*?(router|completeStep|setStepData|getStepData|shouldUseCached)/g,
    severity: 'HIGH',
    message: 'useEffect with function dependencies (router, stepper functions, etc.)',
    fix: 'Use refs to track state, remove function dependencies, or use empty array []',
  },

  // useCallback without empty deps when possible
  unnecessaryCallback: {
    regex: /useCallback\s*\(\s*async\s*\([^)]*\)\s*=>\s*\{[\s\S]*?apiClient\.[^(]+\([^)]*\)[\s\S]*?\},\s*\[[^\]]+\]\s*\)/g,
    severity: 'MEDIUM',
    message: 'useCallback with dependencies that might not be necessary',
    fix: 'Check if dependencies are truly needed, consider using refs',
  },

  // Direct API calls in useEffect without guards
  unguardedApiCall: {
    regex: /useEffect\s*\([^)]*\)\s*=>\s*\{[^}]*apiClient\./g,
    severity: 'HIGH',
    message: 'API call in useEffect without guards (might run multiple times)',
    fix: 'Add refs to track if already fetched: if (hasFetchedRef.current) return;',
  },

  // Router in dependencies
  routerDep: {
    regex: /useEffect\([^)]+\),\s*\[[^\]]*router[^\]]*\]\s*\)/g,
    severity: 'HIGH',
    message: 'useEffect with router in dependencies',
    fix: 'Remove router from dependencies unless navigation is truly needed',
  },

  // Multiple useEffects for same API call
  duplicateEffects: {
    regex: /useEffect[\s\S]{200}useEffect[\s\S]{200}apiClient/g,
    severity: 'MEDIUM',
    message: 'Multiple useEffects in same component might cause duplicate calls',
    fix: 'Combine related effects or use proper guards',
  },

  // localStorage in artifacts (bonus check)
  localStorageInArtifact: {
    regex: /localStorage\.(get|set|remove)/g,
    severity: 'ERROR',
    message: 'localStorage used (not supported in claude.ai artifacts)',
    fix: 'Use React state (useState, useReducer) or window.storage API',
  },
};

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  green: '\x1b[32m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
};

// Results storage
const results = {
  HIGH: [],
  MEDIUM: [],
  ERROR: [],
  filesScanned: 0,
  issuesFound: 0,
};

/**
 * Recursively get all files in directory
 */
function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = fs.readdirSync(dirPath);

  files.forEach((file) => {
    const filePath = path.join(dirPath, file);
    
    if (fs.statSync(filePath).isDirectory()) {
      if (!CONFIG.excludeDirs.includes(file)) {
        arrayOfFiles = getAllFiles(filePath, arrayOfFiles);
      }
    } else {
      const ext = path.extname(file);
      if (CONFIG.fileExtensions.includes(ext)) {
        arrayOfFiles.push(filePath);
      }
    }
  });

  return arrayOfFiles;
}

/**
 * Scan a single file for problematic patterns
 */
function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const fileIssues = [];

  Object.entries(PATTERNS).forEach(([patternName, pattern]) => {
    const matches = content.match(pattern.regex);
    
    if (matches) {
      matches.forEach((match) => {
        // Find line number
        const beforeMatch = content.substring(0, content.indexOf(match));
        const lineNumber = beforeMatch.split('\n').length;

        fileIssues.push({
          file: filePath,
          line: lineNumber,
          pattern: patternName,
          severity: pattern.severity,
          message: pattern.message,
          fix: pattern.fix,
          code: match.substring(0, 100) + (match.length > 100 ? '...' : ''),
        });

        results[pattern.severity].push(fileIssues[fileIssues.length - 1]);
        results.issuesFound++;
      });
    }
  });

  return fileIssues;
}

/**
 * Print results
 */
function printResults() {
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + '           API CALL AUDIT REPORT' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset + '\n');

  console.log(`Files scanned: ${colors.green}${results.filesScanned}${colors.reset}`);
  console.log(`Issues found: ${colors.red}${results.issuesFound}${colors.reset}\n`);

  // Print ERROR issues
  if (results.ERROR.length > 0) {
    console.log(colors.red + '❌ ERROR ISSUES (Must Fix):' + colors.reset);
    results.ERROR.forEach((issue, index) => {
      printIssue(issue, index + 1);
    });
  }

  // Print HIGH severity issues
  if (results.HIGH.length > 0) {
    console.log(colors.red + '\n🔴 HIGH SEVERITY (Causing Multiple API Calls):' + colors.reset);
    results.HIGH.forEach((issue, index) => {
      printIssue(issue, index + 1);
    });
  }

  // Print MEDIUM severity issues
  if (results.MEDIUM.length > 0) {
    console.log(colors.yellow + '\n🟡 MEDIUM SEVERITY (Potential Issues):' + colors.reset);
    results.MEDIUM.forEach((issue, index) => {
      printIssue(issue, index + 1);
    });
  }

  // Summary
  console.log('\n' + colors.cyan + '='.repeat(80) + colors.reset);
  console.log(colors.cyan + 'SUMMARY' + colors.reset);
  console.log(colors.cyan + '='.repeat(80) + colors.reset + '\n');

  const errorCount = results.ERROR.length;
  const highCount = results.HIGH.length;
  const mediumCount = results.MEDIUM.length;

  if (errorCount > 0) {
    console.log(colors.red + `❌ ${errorCount} ERROR issues` + colors.reset);
  }
  if (highCount > 0) {
    console.log(colors.red + `🔴 ${highCount} HIGH severity issues` + colors.reset);
  }
  if (mediumCount > 0) {
    console.log(colors.yellow + `🟡 ${mediumCount} MEDIUM severity issues` + colors.reset);
  }
  if (errorCount === 0 && highCount === 0 && mediumCount === 0) {
    console.log(colors.green + '✅ No issues found! Great job!' + colors.reset);
  }

  console.log('\n' + colors.gray + 'Recommendations:' + colors.reset);
  console.log(colors.gray + '1. Fix ERROR issues immediately' + colors.reset);
  console.log(colors.gray + '2. Fix HIGH severity issues to reduce API calls' + colors.reset);
  console.log(colors.gray + '3. Review MEDIUM severity issues for potential improvements' + colors.reset);
  console.log(colors.gray + '4. Run this script after fixes to verify' + colors.reset + '\n');
}

/**
 * Print individual issue
 */
function printIssue(issue, number) {
  const color = issue.severity === 'ERROR' ? colors.red : 
                issue.severity === 'HIGH' ? colors.red : colors.yellow;
  
  console.log(`\n${color}Issue #${number}${colors.reset}`);
  console.log(`${colors.gray}File:${colors.reset} ${issue.file}:${issue.line}`);
  console.log(`${colors.gray}Pattern:${colors.reset} ${issue.pattern}`);
  console.log(`${colors.gray}Problem:${colors.reset} ${issue.message}`);
  console.log(`${colors.gray}Fix:${colors.reset} ${issue.fix}`);
  console.log(`${colors.gray}Code:${colors.reset}`);
  console.log(colors.gray + issue.code.trim() + colors.reset);
}

/**
 * Generate fix suggestions file
 */
function generateFixSuggestions() {
  const suggestions = [];

  results.HIGH.forEach((issue) => {
    suggestions.push({
      file: issue.file,
      line: issue.line,
      problem: issue.message,
      fix: issue.fix,
      priority: 'HIGH',
    });
  });

  results.MEDIUM.forEach((issue) => {
    suggestions.push({
      file: issue.file,
      line: issue.line,
      problem: issue.message,
      fix: issue.fix,
      priority: 'MEDIUM',
    });
  });

  if (suggestions.length > 0) {
    const output = JSON.stringify(suggestions, null, 2);
    fs.writeFileSync('./api-audit-fixes.json', output);
    console.log(colors.green + '✅ Fix suggestions saved to: api-audit-fixes.json' + colors.reset);
  }
}

/**
 * Main execution
 */
function main() {
  console.log(colors.cyan + '\n🔍 Scanning for API call issues...\n' + colors.reset);

  const files = getAllFiles(CONFIG.searchDir);
  results.filesScanned = files.length;

  files.forEach((file) => {
    scanFile(file);
  });

  printResults();
  generateFixSuggestions();

  // Exit with error code if high severity issues found
  if (results.ERROR.length > 0 || results.HIGH.length > 0) {
    process.exit(1);
  }
}

// Run the audit
main();