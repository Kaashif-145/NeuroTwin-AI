import os
import re
import ast
from backend.utils.llm_client import get_chat_response

def analyze_python_syntax(code_text):
    """Checks for syntax and indentation errors in Python code."""
    try:
        ast.parse(code_text)
        return None, None
    except SyntaxError as e:
        return e.lineno, e.msg
    except Exception as e:
        return 1, str(e)

def check_code_quality(code_text, language="Python"):
    """
    Analyzes code for quality and detects if the language matches the selection.
    """
    if not code_text:
        return "No code provided."

    system_prompt = (
        f"You are a Senior Software Architect and strict Code Reviewer. Your task is to analyze this code. "
        f"FIRST, verify if this code is actually written in {language}. If it is NOT, start your response with 'LANGUAGE_MISMATCH: [Detected Language]'.\n\n"
        "Otherwise, provide:\n"
        "1. ### 📝 Teacher's Remarks: Be brutal and blunt about mistakes. Directly point out missing base cases, infinite loops, runtime exceptions, and logic errors. Do not be lenient.\n"
        "2. ### 💻 Expected Output: Simulate the terminal output (if it would crash with RecursionError or infinite loop, say so clearly).\n"
        "3. ### 🛠️ The Perfected Solution: Provide the optimized, bug-free code.\n"
    )
    
    try:
        response, _ = get_chat_response(
            prompt=f"Analyze this code. Selected language is {language}:\n\n```\n{code_text}\n```",
            system_prefix=system_prompt,
            allow_wolfram=False
        )
        return response
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def detect_python_logic_errors(code_text):
    """Uses AST to detect common logic errors like infinite recursion or infinite loops."""
    errors = []
    try:
        tree = ast.parse(code_text)
    except:
        return errors # Syntax errors handled separately

    for node in ast.walk(tree):
        # Detect infinite recursion (missing base case)
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            calls_self = False
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id == func_name:
                        calls_self = True
                        break
            
            if calls_self:
                has_base_case = False
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        # A very basic check: is there a return or raise inside the if?
                        for if_child in ast.walk(child):
                            if isinstance(if_child, (ast.Return, ast.Raise)):
                                has_base_case = True
                                break
                if not has_base_case:
                    errors.append(f"Infinite Recursion: Function '{func_name}' calls itself but lacks a base case (an 'if' statement with a 'return').")

        # Detect obvious infinite loops (while True without break/return)
        if isinstance(node, ast.While):
            # Check if condition is always True
            is_always_true = False
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                is_always_true = True
            
            if is_always_true:
                has_break = False
                for child in ast.walk(node):
                    if isinstance(child, (ast.Break, ast.Return)):
                        has_break = True
                        break
                if not has_break:
                    errors.append("Infinite Loop: 'while True' loop found without a 'break' or 'return' statement.")

    return errors
def detect_general_logic_errors(code_text, language):
    """Uses Regex and basic parsing to detect common logic errors in C/C++/Java/C#/JS."""
    errors = []
    
    # Strip out single line and multi-line comments so they don't interfere with logic parsing
    clean_code = re.sub(r'//.*', '', code_text)
    clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)
    
    # 1. Infinite loop check (while(true) without break/return)
    while_true_matches = re.finditer(r'while\s*\(\s*(true|1)\s*\)\s*\{([^}]*)\}', clean_code, re.IGNORECASE)
    for match in while_true_matches:
        block = match.group(2)
        if 'break' not in block and 'return' not in block:
            errors.append("Infinite Loop: 'while(true)' loop found without a 'break' or 'return'.")
            
    # 2. Check for missing base cases in basic recursion and incomplete algorithms
    func_matches = re.finditer(r'\b([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{', clean_code)
    for match in func_matches:
        func_name = match.group(1)
        if func_name.lower() in ['if', 'while', 'for', 'switch', 'catch', 'else']:
            continue
            
        start_idx = match.end()
        brace_count = 1
        end_idx = start_idx
        for i in range(start_idx, len(clean_code)):
            if clean_code[i] == '{':
                brace_count += 1
            elif clean_code[i] == '}':
                brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break
        
        if brace_count == 0:
            body = clean_code[start_idx:end_idx]
            
            # Check for infinite recursion
            if re.search(r'\b' + re.escape(func_name) + r'\s*\(', body):
                # It calls itself. Check for an 'if' followed by 'return'
                if not re.search(r'if\s*\(.*?\).*?return', body, re.DOTALL | re.IGNORECASE) and not re.search(r'return.*?if', body, re.DOTALL | re.IGNORECASE):
                    errors.append(f"Infinite Recursion: Function '{func_name}' calls itself but lacks a visible base case (an 'if' with a 'return').")
            
            # Check for totally incomplete algorithms (no loops, no recursion)
            is_expected_recursive = any(name in func_name.lower() for name in ['sort', 'search', 'dfs', 'bfs', 'fib', 'traverse'])
            if is_expected_recursive:
                has_loop = re.search(r'\b(for|while)\b', body)
                has_recursion = re.search(r'\b' + re.escape(func_name) + r'\s*\(', body)
                if not has_loop and not has_recursion:
                    errors.append(f"Logic Error: Algorithm '{func_name}' is expected to iterate or recurse, but does neither.")
    
    # 3. Missing Return Types in C/C++/Java/C# (e.g. `static mergesort(list)`)
    if language in ["C", "C++", "Java", "C#"]:
        modifiers = r'\b(public|private|protected|static|virtual|inline|internal|override)\b'
        bad_funcs = re.finditer(rf'{modifiers}\s+([a-z]\w*)\s*\(', clean_code)
        for match in bad_funcs:
            errors.append(f"Syntax Error: Missing return type for method '{match.group(2)}'.")

    # 4. Missing Semicolons
    if language in ["C", "C++", "Java", "C#"]:
        lines = code_text.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.startswith("/*") and not stripped.startswith("*") and not stripped.startswith("#"):
                if not stripped.endswith(";") and not stripped.endswith("{") and not stripped.endswith("}") and not stripped.endswith(":") and not stripped.endswith(","):
                    if "=" in stripped or ("(" in stripped and ")" in stripped):
                        # Exclude control flow structures that don't need semicolons
                        if not any(stripped.startswith(kw) for kw in ['if', 'while', 'for', 'else', 'switch', 'catch', 'public', 'private', 'static']):
                            errors.append(f"Syntax Error: Possible missing semicolon at line {i+1}.")
                            break
                            
    return errors

def local_offline_analysis(code_text, language="C"):
    """Provides a basic rule-based analysis when AI is offline."""
    remarks = "### 📝 Local Analysis (AI Offline)\n"
    score = 100
    
    if language.lower() == "python":
        lineno, msg = analyze_python_syntax(code_text)
        if msg:
            remarks += f"- ❌ ERROR: Syntax/Indentation error detected at line {lineno}: {msg}.\n"
            score -= 100
        else:
            logic_errors = detect_python_logic_errors(code_text)
            for err in logic_errors:
                remarks += f"- ❌ LOGIC ERROR: {err}\n"
                score -= 70
    else:
        # Check for basic completeness in other languages
        if code_text.count('{') != code_text.count('}'):
            remarks += "- ❌ ERROR: Unbalanced curly braces detected.\n"
            score -= 50
            
        general_errors = detect_general_logic_errors(code_text, language)
        for err in general_errors:
            if "Syntax Error" in err:
                remarks += f"- ❌ {err}\n"
                score -= 100
            else:
                remarks += f"- ❌ LOGIC ERROR: {err}\n"
                score -= 70

    if len(code_text.splitlines()) < 5:
        remarks += "- ⚠️ WARNING: Code seems incomplete or too short.\n"
        score -= 20
        
    if score == 100:
        remarks += "- ✅ Basic structure looks valid and complete.\n"
    elif score >= 70:
        remarks += "- ✅ Basic structure looks valid but has warnings.\n"
    else:
        remarks += "- ❌ CRITICAL: Code has major structural or logical errors.\n"
    
    remarks += "\n### 🛠️ Note: For full architectural feedback and deep logic checks, please wait for AI Quota reset."
    return remarks, max(0, score)

def evaluate_code_score(code_text, language="Python"):
    """
    Returns an objective score (0-100). Uses local fallback if AI is down.
    """
    system_prompt = (
        f"You are an extremely strict, unforgiving Code Reviewer. Grade this {language} code on a scale of 0 to 100. "
        "Apply these CRITICAL DEDUCTIONS strictly. If multiple apply, return the lowest score:\n"
        "- Infinite loops or missing base cases in recursion: RETURN 10\n"
        "- Will throw runtime exceptions (e.g., Index out of bounds, ZeroDivisionError, RecursionError): RETURN 20\n"
        "- Major logic errors or incorrect algorithm implementation: RETURN 30\n"
        "- Syntax errors or incomplete code: RETURN 0\n"
        "- Poor performance or non-optimal time complexity (e.g. O(N^2) instead of O(N log N)): RETURN 60\n"
        "- Perfectly optimal, bug-free, and handles all edge cases: RETURN 100\n"
        "Even if the code contains comments explaining errors, you MUST grade the code as if the comments are not there and the error will happen during execution. "
        "Return ONLY the final numeric score (e.g. 10). Do not provide any explanation."
    )
    try:
        response, _ = get_chat_response(
            prompt=f"Grade this code strictly:\n\n{code_text}", 
            system_prefix=system_prompt,
            allow_wolfram=False
        )
        match = re.search(r'\d+', response)
        if match:
            return int(match.group(0))
        return 0
    except:
        # 🚀 Use Local Fallback so the user isn't stuck at 0/NA
        _, local_score = local_offline_analysis(code_text, language)
        return local_score
