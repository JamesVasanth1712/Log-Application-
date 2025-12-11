# from flask import Flask, render_template, request, jsonify
# import pandas as pd
# import os
# from datetime import datetime
# import re
# from collections import Counter

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# # Ensure upload folder exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# class LogParser:
#     @staticmethod
#     def extract_user_from_message(line):
#         # Try to extract username from common patterns
#         patterns = [
#             r'user[=:]\s*(\w+)',
#             r'username[=:]\s*(\w+)',
#             r'for\s+(\w+)\s+from',
#             r'user\s+(\w+)',
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, line, re.IGNORECASE)
#             if match:
#                 return match.group(1)
#         return None

#     @staticmethod
#     def parse_line(line, log_type=None):
#         parsers = {
#             'apache': LogParser.parse_apache,
#             'nginx': LogParser.parse_nginx,
#             'docker': LogParser.parse_docker,
#             'mongodb': LogParser.parse_mongodb,
#             'mysql': LogParser.parse_mysql,
#             'postgresql': LogParser.parse_postgresql,
#             'redis': LogParser.parse_redis,
#             'ejabberd': LogParser.parse_ejabberd,
#         }

#         # If specific log type is requested, try that parser first
#         if log_type and log_type in parsers and log_type != 'auto':
#             result = parsers[log_type](line)
#             if result:
#                 return result
#             # If Apache parser fails, still try to extract status codes from the line
#             if log_type == 'apache':
#                 # Last resort: try to find any HTTP status code in the line
#                 # Look for patterns like: "HTTP/1.x" 200 or just 3-digit codes after quotes
#                 status_patterns = [
#                     r'HTTP/\d\.\d"\s+(\d{3})',  # After HTTP version
#                     r'"\s+(\d{3})\s+',  # After closing quote
#                     r'\b([4-5]\d{2})\b',  # 4xx or 5xx codes
#                     r'\b([2-3]\d{2})\b',  # 2xx or 3xx codes
#                 ]
                
#                 status = None
#                 for pattern in status_patterns:
#                     status_match = re.search(pattern, line)
#                     if status_match:
#                         try:
#                             status = int(status_match.group(1))
#                             if 200 <= status <= 599:
#                                 break
#                         except (ValueError, IndexError):
#                             continue
                
#                 if status and 200 <= status <= 599:
#                     # Map status to level
#                     if status >= 500:
#                         level = 'ERROR'
#                     elif status >= 400:
#                         level = 'WARN'
#                     elif status >= 300:
#                         level = 'NOTICE'
#                     else:
#                         level = 'INFO'
                    
#                     # Extract basic fields
#                     ip_match = re.search(r'^(\S+)', line)
#                     timestamp_match = re.search(r'\[(.*?)\]', line)
#                     method_match = re.search(r'"(\w+)', line)
                    
#                     return {
#                         'timestamp': timestamp_match.group(1) if timestamp_match else datetime.now().isoformat(),
#                         'ip': ip_match.group(1) if ip_match else 'unknown',
#                         'method': method_match.group(1) if method_match else 'UNKNOWN',
#                         'path': 'unknown',
#                         'status': status,
#                         'level': level,
#                         'message': f"{method_match.group(1) if method_match else 'UNKNOWN'} unknown - {status}",
#                         'user': None
#                     }

#         # Auto-detect: try all parsers
#         for parser in parsers.values():
#             try:
#                 result = parser(line)
#             except Exception:
#                 result = None
#             if result:
#                 return result

#         return LogParser.parse_generic(line)

#     @staticmethod
#     def parse_apache(line):
#         # Try multiple Apache log patterns
#         # Common Apache Combined Log Format: IP - - [timestamp] "method path protocol" status size
#         status = None
#         ip = None
#         timestamp = None
#         method = None
#         path = None
        
#         # Pattern 1: Standard Combined Log Format with size: IP - - [timestamp] "method path HTTP/1.x" status size
#         pattern1 = r'(\S+) - - \[(.*?)\] "(\w+) (.*?) HTTP/\d\.\d" (\d+) (\d+)'
#         match = re.search(pattern1, line)
#         if match:
#             try:
#                 status = int(match.group(5))
#                 ip = match.group(1)
#                 timestamp = match.group(2)
#                 method = match.group(3)
#                 path = match.group(4)
#             except (ValueError, IndexError):
#                 match = None
        
#         # Pattern 2: Combined Log Format with user: IP - user [timestamp] "method path HTTP/1.x" status size
#         if not match:
#             pattern2 = r'(\S+) - (\S+) \[(.*?)\] "(\w+) (.*?) HTTP/\d\.\d" (\d+) (\d+)'
#             match = re.search(pattern2, line)
#             if match:
#                 try:
#                     status = int(match.group(6))
#                     ip = match.group(1)
#                     timestamp = match.group(3)
#                     method = match.group(4)
#                     path = match.group(5)
#                 except (ValueError, IndexError):
#                     match = None
        
#         # Pattern 3: Without size field: IP - - [timestamp] "method path HTTP/1.x" status
#         if not match:
#             pattern3 = r'(\S+) - - \[(.*?)\] "(\w+) (.*?) HTTP/\d\.\d" (\d+)'
#             match = re.search(pattern3, line)
#             if match:
#                 try:
#                     status = int(match.group(5))
#                     ip = match.group(1)
#                     timestamp = match.group(2)
#                     method = match.group(3)
#                     path = match.group(4)
#                 except (ValueError, IndexError):
#                     match = None
        
#         # Pattern 4: More flexible - any HTTP status code in the line
#         if not match:
#             # Look for HTTP status code pattern: "HTTP/1.x" status or just status after quotes
#             status_match = re.search(r'HTTP/\d\.\d"\s+(\d{3})', line)
#             if status_match:
#                 try:
#                     status = int(status_match.group(1))
#                     # Try to extract other fields with a more flexible pattern
#                     ip_match = re.search(r'^(\S+)', line)
#                     timestamp_match = re.search(r'\[(.*?)\]', line)
#                     method_match = re.search(r'"(\w+)', line)
#                     path_match = re.search(r'"\w+\s+(.*?)\s+HTTP', line)
                    
#                     ip = ip_match.group(1) if ip_match else None
#                     timestamp = timestamp_match.group(1) if timestamp_match else None
#                     method = method_match.group(1) if method_match else None
#                     path = path_match.group(1) if path_match else None
#                     match = True
#                 except (ValueError, IndexError):
#                     match = None
        
#         # Pattern 5: Even more flexible - find any 3-digit status code that looks like HTTP status
#         if not match:
#             # Look for 3-digit numbers that are likely HTTP status codes (200-599)
#             # Try multiple patterns to catch status codes in different positions
#             status_patterns = [
#                 r'"\s+(\d{3})\s+',  # After closing quote, before size
#                 r'HTTP/\d\.\d"\s+(\d{3})',  # After HTTP version
#                 r'\b([4-5]\d{2})\b',  # 4xx or 5xx codes anywhere
#                 r'\b([2-3]\d{2})\b',  # 2xx or 3xx codes anywhere
#             ]
            
#             for pattern in status_patterns:
#                 status_match = re.search(pattern, line)
#                 if status_match:
#                     try:
#                         status = int(status_match.group(1))
#                         if 200 <= status <= 599:
#                             # Try to extract basic fields
#                             ip_match = re.search(r'^(\S+)', line)
#                             timestamp_match = re.search(r'\[(.*?)\]', line)
#                             method_match = re.search(r'"(\w+)', line)
                            
#                             ip = ip_match.group(1) if ip_match else None
#                             timestamp = timestamp_match.group(1) if timestamp_match else None
#                             method = method_match.group(1) if method_match else None
#                             path = "unknown"
#                             match = True
#                             break
#                     except (ValueError, IndexError):
#                         continue
        
#         # If we found a status code, create the result
#         if status is not None:
#             # Map HTTP status codes to log levels (matching Grafana-style classification)
#             if status >= 500:
#                 level = 'ERROR'
#             elif status >= 400:
#                 level = 'WARN'
#             elif status >= 300:
#                 level = 'NOTICE'  # Redirects (301, 302, etc.)
#             elif status >= 200:
#                 level = 'INFO'    # Success (200, 201, etc.)
#             else:
#                 level = 'INFO'
            
#             message = f"{method or 'UNKNOWN'} {path or 'unknown'} - {status}"
#             return {
#                 'timestamp': timestamp or datetime.now().isoformat(),
#                 'ip': ip or 'unknown',
#                 'method': method or 'UNKNOWN',
#                 'path': path or 'unknown',
#                 'status': status,  # Make sure status is always included
#                 'level': level,
#                 'message': message,
#                 'user': LogParser.extract_user_from_message(line)
#             }
        
#         # Last resort: if this looks like an Apache log but no pattern matched,
#         # try to find ANY 3-digit number that could be a status code
#         if '"' in line or 'HTTP' in line.upper():
#             # Find all 3-digit numbers
#             all_numbers = re.findall(r'\b(\d{3})\b', line)
#             for num_str in all_numbers:
#                 try:
#                     num = int(num_str)
#                     if 200 <= num <= 599:  # Valid HTTP status code range
#                         status = num
#                         # Map to level
#                         if status >= 500:
#                             level = 'ERROR'
#                         elif status >= 400:
#                             level = 'WARN'
#                         elif status >= 300:
#                             level = 'NOTICE'
#                         else:
#                             level = 'INFO'
                        
#                         # Extract basic fields
#                         ip_match = re.search(r'^(\S+)', line)
#                         timestamp_match = re.search(r'\[(.*?)\]', line)
#                         method_match = re.search(r'"(\w+)', line)
                        
#                         return {
#                             'timestamp': timestamp_match.group(1) if timestamp_match else datetime.now().isoformat(),
#                             'ip': ip_match.group(1) if ip_match else 'unknown',
#                             'method': method_match.group(1) if method_match else 'UNKNOWN',
#                             'path': 'unknown',
#                             'status': status,  # Make sure status is always included
#                             'level': level,
#                             'message': f"{method_match.group(1) if method_match else 'UNKNOWN'} unknown - {status}",
#                             'user': None
#                         }
#                 except (ValueError, IndexError):
#                     continue
        
#         return None

#     @staticmethod
#     def parse_nginx(line):
#         pattern = r'(\S+) - \S+ \[(.*?)\] "(\w+) (.*?) HTTP/\d\.\d" (\d+) (\d+)'
#         match = re.search(pattern, line)
#         if match:
#             status = int(match.group(5))
#             level = 'ERROR' if status >= 500 else 'WARN' if status >= 400 else 'NOTICE' if status >= 300 else 'INFO'
#             return {
#                 'timestamp': match.group(2),
#                 'ip': match.group(1),
#                 'method': match.group(3),
#                 'path': match.group(4),
#                 'status': status,
#                 'level': level,
#                 'message': f"{match.group(3)} {match.group(4)} - {status}",
#                 'user': LogParser.extract_user_from_message(line)
#             }
#         return None

#     @staticmethod
#     def parse_docker(line):
#         match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if re.search(r'\b(error|exception|failed)\b', line, re.IGNORECASE) else \
#                 'WARN' if re.search(r'\b(warn|warning)\b', line, re.IGNORECASE) else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_mongodb(line):
#         match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if re.search(r'\b(E |ERROR|exception|failed)\b', line, re.IGNORECASE) else \
#                 'WARN' if re.search(r'\b(W |WARN|Warning)\b', line, re.IGNORECASE) else \
#                 'NOTICE' if 'NOTICE' in line.upper() else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_mysql(line):
#         match = re.search(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if re.search(r'\bERROR\b', line, re.IGNORECASE) else \
#                 'WARN' if re.search(r'\bWARN|Warning\b', line, re.IGNORECASE) else \
#                 'NOTICE' if re.search(r'\bNOTICE\b', line, re.IGNORECASE) else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_postgresql(line):
#         match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if re.search(r'\bERROR|FATAL\b', line, re.IGNORECASE) else \
#                 'WARN' if re.search(r'\bWARNING\b', line, re.IGNORECASE) else \
#                 'NOTICE' if re.search(r'\bNOTICE\b', line, re.IGNORECASE) else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_redis(line):
#         match = re.search(r'(\d{2} \w+ \d{4} \d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if '#' in line[:30] else 'WARN' if '*' in line[:30] else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_ejabberd(line):
#         match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
#         timestamp = match.group(1) if match else datetime.now().isoformat()
#         level = 'ERROR' if 'error' in line.lower() else 'WARN' if 'warn' in line.lower() else 'INFO'
#         return {
#             'timestamp': timestamp,
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }

#     @staticmethod
#     def parse_generic(line):
#         level_match = re.search(r'\b(ERROR|WARN|WARNING|INFO|DEBUG|CRITICAL|FATAL|NOTICE)\b', line, re.IGNORECASE)
#         level = level_match.group(1).upper() if level_match else 'INFO'
#         if level == 'WARN':
#             level = 'WARNING'
#         if level == 'FATAL':
#             level = 'ERROR'
#         return {
#             'timestamp': datetime.now().isoformat(),
#             'level': level,
#             'message': line.strip(),
#             'user': LogParser.extract_user_from_message(line)
#         }


# class LogAnalyzer:
#     def __init__(self, log_type='auto'):
#         self.log_type = log_type
#         self.data = []

#     def analyze_file(self, filepath):
#         ext = filepath.rsplit('.', 1)[-1].lower()
#         try:
#             if ext in ['txt', 'log']:
#                 parsed_count = 0
#                 skipped_count = 0
#                 status_codes_found = []
#                 levels_found = []
#                 with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
#                     for line_num, line in enumerate(f, 1):
#                         if line.strip():
#                             parsed = LogParser.parse_line(line, self.log_type)
#                             if parsed:
#                                 # For Apache logs, if no status code was extracted, try to extract it from the raw line
#                                 if self.log_type == 'apache' and 'status' not in parsed:
#                                     # Try to find status code in the raw line
#                                     status_match = re.search(r'\b(\d{3})\b', line)
#                                     if status_match:
#                                         try:
#                                             status = int(status_match.group(1))
#                                             if 200 <= status <= 599:
#                                                 parsed['status'] = status
#                                                 # Update level based on status
#                                                 if status >= 500:
#                                                     parsed['level'] = 'ERROR'
#                                                 elif status >= 400:
#                                                     parsed['level'] = 'WARN'
#                                                 elif status >= 300:
#                                                     parsed['level'] = 'NOTICE'
#                                                 else:
#                                                     parsed['level'] = 'INFO'
#                                         except (ValueError, IndexError):
#                                             pass
                                
#                                 self.data.append(parsed)
#                                 parsed_count += 1
#                                 # Collect status codes and levels for debugging
#                                 if 'status' in parsed:
#                                     status_codes_found.append(parsed['status'])
#                                 if 'level' in parsed:
#                                     levels_found.append(parsed['level'])
#                                 # Show first few parsed lines for debugging
#                                 if parsed_count <= 3:
#                                     print(f"DEBUG: Parsed line {line_num}: status={parsed.get('status', 'N/A')}, level={parsed.get('level', 'N/A')}")
#                             else:
#                                 # If parsing failed but this is an Apache log, try to extract status code anyway
#                                 if self.log_type == 'apache':
#                                     status_match = re.search(r'\b(\d{3})\b', line)
#                                     if status_match:
#                                         try:
#                                             status = int(status_match.group(1))
#                                             if 200 <= status <= 599:
#                                                 # Create a minimal parsed record with status code
#                                                 if status >= 500:
#                                                     level = 'ERROR'
#                                                 elif status >= 400:
#                                                     level = 'WARN'
#                                                 elif status >= 300:
#                                                     level = 'NOTICE'
#                                                 else:
#                                                     level = 'INFO'
                                                
#                                                 ip_match = re.search(r'^(\S+)', line)
#                                                 timestamp_match = re.search(r'\[(.*?)\]', line)
                                                
#                                                 parsed = {
#                                                     'timestamp': timestamp_match.group(1) if timestamp_match else datetime.now().isoformat(),
#                                                     'ip': ip_match.group(1) if ip_match else 'unknown',
#                                                     'status': status,
#                                                     'level': level,
#                                                     'message': line.strip()[:200],
#                                                     'user': None
#                                                 }
#                                                 self.data.append(parsed)
#                                                 parsed_count += 1
#                                                 status_codes_found.append(status)
#                                                 levels_found.append(level)
#                                                 continue
#                                         except (ValueError, IndexError):
#                                             pass
                                
#                                 skipped_count += 1
#                                 # Debug: show first few unparsed lines
#                                 if skipped_count <= 3:
#                                     print(f"DEBUG: Skipped line {line_num}: {line[:100]}")
                
#                 print(f"DEBUG: Parsed {parsed_count} lines, skipped {skipped_count} lines")
#                 if status_codes_found:
#                     from collections import Counter
#                     status_dist = Counter(status_codes_found)
#                     level_dist = Counter(levels_found)
#                     print(f"DEBUG: Status codes found: {dict(status_dist.most_common(10))}")
#                     print(f"DEBUG: Levels found: {dict(level_dist)}")
#                 else:
#                     print(f"DEBUG: WARNING - No status codes found in parsed data!")
#                     if parsed_count > 0 and skipped_count == 0:
#                         # All lines parsed but no status codes - show sample of parsed data
#                         print(f"DEBUG: Sample parsed record: {self.data[0] if self.data else 'No data'}")
#             elif ext == 'csv':
#                 df = pd.read_csv(filepath)
#                 df.columns = [str(c).strip().lower() for c in df.columns]
#                 for _, row in df.iterrows():
#                     record = row.to_dict()
#                     record.setdefault('level', 'INFO')
#                     record.setdefault('timestamp', datetime.now().isoformat())
#                     record.setdefault('message', str(row))
#                     self.data.append(record)
#             elif ext == 'xlsx':
#                 df = pd.read_excel(filepath)
#                 df.columns = [str(c).strip().lower() for c in df.columns]
#                 for _, row in df.iterrows():
#                     record = row.to_dict()
#                     record.setdefault('level', 'INFO')
#                     record.setdefault('timestamp', datetime.now().isoformat())
#                     record.setdefault('message', str(row))
#                     self.data.append(record)
#         except Exception as e:
#             print(f"Error reading file: {str(e)}")
#             raise

#     def generate_insights(self):
#         if not self.data:
#             return None

#         df = pd.DataFrame(self.data)
#         df['level'] = df['level'].astype(str).str.upper().str.strip()
#         df['level'] = df['level'].replace('NAN', 'INFO')
        
#         # convert timestamp to dt
#         df['timestamp'] = df.get('timestamp', pd.Series([None]*len(df)))
#         df['dt'] = pd.to_datetime(df['timestamp'], errors='coerce')

#         total = len(df)
        
#         # For Apache/nginx logs, also count by status codes if level counting fails
#         # This ensures accurate counts even if level field wasn't set correctly
#         errors = 0
#         warnings = 0
#         notices = 0
#         info = 0
        
#         # First, try counting by level field
#         if 'level' in df.columns:
#             errors = int(len(df[df['level'].isin(['ERROR', 'FATAL', 'CRITICAL'])]))
#             warnings = int(len(df[df['level'].isin(['WARN', 'WARNING'])]))
#             notices = int(len(df[df['level'] == 'NOTICE']))
#             info = int(len(df[df['level'] == 'INFO']))
        
#         # If we have status codes, count by status codes (more reliable for Apache/nginx logs)
#         # This ensures accurate counts even if level field wasn't set correctly
#         if 'status' in df.columns:
#             # Convert status to numeric, handling any non-numeric values
#             df['status_num'] = pd.to_numeric(df['status'], errors='coerce')
            
#             # Check how many valid status codes we have
#             valid_status_count = df['status_num'].notna().sum()
#             print(f"DEBUG: Found {valid_status_count} records with status codes out of {total} total")
            
#             if valid_status_count > 0:
#                 # Count by HTTP status codes directly
#                 status_errors = int(len(df[df['status_num'] >= 500]))
#                 status_warnings = int(len(df[(df['status_num'] >= 400) & (df['status_num'] < 500)]))
#                 status_notices = int(len(df[(df['status_num'] >= 300) & (df['status_num'] < 400)]))
#                 status_info = int(len(df[(df['status_num'] >= 200) & (df['status_num'] < 300)]))
                
#                 print(f"DEBUG: Status-based counts - Errors: {status_errors}, Warnings: {status_warnings}, Notices: {status_notices}, Info: {status_info}")
                
#                 # Use status code counts if they're more accurate (non-zero) or if level counts are all 0
#                 if (status_errors > 0 or status_warnings > 0 or status_notices > 0) or (errors == 0 and warnings == 0 and notices == 0):
#                     errors = status_errors
#                     warnings = status_warnings
#                     notices = status_notices
#                     info = status_info
                    
#                     # Also update the level field based on status codes for consistency
#                     df.loc[df['status_num'] >= 500, 'level'] = 'ERROR'
#                     df.loc[(df['status_num'] >= 400) & (df['status_num'] < 500), 'level'] = 'WARN'
#                     df.loc[(df['status_num'] >= 300) & (df['status_num'] < 400), 'level'] = 'NOTICE'
#                     df.loc[(df['status_num'] >= 200) & (df['status_num'] < 300), 'level'] = 'INFO'
#             else:
#                 print(f"DEBUG: WARNING - 'status' column exists but contains no valid numeric values!")
#                 print(f"DEBUG: Sample status values: {df['status'].head(10).tolist()}")
        
#         # If still all 0, try contains method as fallback
#         if errors == 0 and warnings == 0 and notices == 0 and info == 0:
#             # Use contains method with proper NaN handling
#             level_series = df['level'].astype(str)
#             errors = int(len(df[level_series.str.contains('ERROR|FATAL|CRITICAL', case=False, na=False, regex=True)]))
#             warnings = int(len(df[level_series.str.contains('WARN', case=False, na=False, regex=True)]))
#             notices = int(len(df[level_series.str.contains('NOTICE', case=False, na=False, regex=True)]))
#             info = int(len(df[level_series.str.contains('INFO', case=False, na=False, regex=True)]))
        
#         # Debug output
#         print(f"DEBUG: Total logs: {total}")
#         if 'status' in df.columns:
#             print(f"DEBUG: Status code distribution: {df['status'].value_counts().head(10).to_dict()}")
#         print(f"DEBUG: Level value counts: {df['level'].value_counts().to_dict()}")
#         print(f"DEBUG: Errors: {errors}, Warnings: {warnings}, Notices: {notices}, Info: {info}")

#         level_dist = df['level'].value_counts().to_dict()

#         # time series
#         time_data = []
#         valid = df[df['dt'].notna()]
#         if len(valid) > 0:
#             valid['hour'] = valid['dt'].dt.hour
#             hourly = valid.groupby('hour').size()
#             time_data = [{'hour': int(h), 'count': int(c)} for h, c in hourly.items()]
#             time_data.sort(key=lambda x: x['hour'])

#         # top errors
#         error_list = []
#         if 'message' in df.columns:
#             err_df = df[df['level'].str.contains('ERROR', case=False, na=False)]
#             if len(err_df) > 0:
#                 counts = err_df['message'].value_counts().head(20)
#                 error_list = [{'message': str(m)[:200], 'count': int(c)} for m, c in counts.items()]

#         # status codes & ips
#         status_list = []
#         if 'status' in df.columns:
#             # Filter out NaN/null values and convert to numeric
#             status_df = df[df['status'].notna()].copy()
#             if len(status_df) > 0:
#                 # Convert to numeric, handling any string values
#                 status_df['status_num'] = pd.to_numeric(status_df['status'], errors='coerce')
#                 status_df = status_df[status_df['status_num'].notna()]
#                 if len(status_df) > 0:
#                     counts = status_df['status_num'].value_counts().head(20)
#                     status_list = [{'status': str(int(s)), 'count': int(c)} for s, c in counts.items()]

#         ip_list = []
#         if 'ip' in df.columns:
#             counts = df['ip'].value_counts().head(20)
#             ip_list = [{'ip': str(ip), 'count': int(c)} for ip, c in counts.items()]

#         # DB-specific heuristics (only meaningful for DB log types)
#         # failed logins detection
#         failed_patterns = [
#             re.compile(r'access denied', re.IGNORECASE),
#             re.compile(r'authentication failed', re.IGNORECASE),
#             re.compile(r'login failed', re.IGNORECASE),
#             re.compile(r'failed password', re.IGNORECASE),
#             re.compile(r'invalid password', re.IGNORECASE),
#         ]
#         failed_logins = 0
#         failed_login_examples = []
#         if 'message' in df.columns:
#             for _, row in df.iterrows():
#                 msg = str(row.get('message', ''))
#                 for pattern in failed_patterns:
#                     if pattern.search(msg):
#                         failed_logins += 1
#                         if len(failed_login_examples) < 10:
#                             failed_login_examples.append({
#                                 'message': msg[:200],
#                                 'count': 1
#                             })
#                         break

#         # unique users
#         unique_users = 0
#         top_users = []
#         if 'user' in df.columns:
#             user_df = df[df['user'].notna()]
#             if len(user_df) > 0:
#                 unique_users = user_df['user'].nunique()
#                 counts = user_df['user'].value_counts().head(10)
#                 top_users = [{'user': str(u), 'count': int(c)} for u, c in counts.items()]

#         # active users (24h)
#         active_users_24h = 0
#         if 'user' in df.columns and 'dt' in df.columns:
#             user_time_df = df[(df['user'].notna()) & (df['dt'].notna())]
#             if len(user_time_df) > 0:
#                 now = pd.Timestamp.now()
#                 last_24h = user_time_df[user_time_df['dt'] >= (now - pd.Timedelta(hours=24))]
#                 active_users_24h = last_24h['user'].nunique() if len(last_24h) > 0 else 0

#         # query errors
#         query_error_patterns = [
#             re.compile(r'syntax error', re.IGNORECASE),
#             re.compile(r'query failed', re.IGNORECASE),
#             re.compile(r'sql error', re.IGNORECASE),
#         ]
#         total_query_errors = 0
#         if 'message' in df.columns:
#             for _, row in df.iterrows():
#                 msg = str(row.get('message', ''))
#                 for pattern in query_error_patterns:
#                     if pattern.search(msg):
#                         total_query_errors += 1
#                         break

#         # root causes
#         root_causes = []
#         if errors > total * 0.1:
#             root_causes.append(f"High error rate detected: {errors} errors ({errors/total*100:.1f}% of total logs)")
#         if warnings > total * 0.2:
#             root_causes.append(f"Moderate warning rate: {warnings} warnings ({warnings/total*100:.1f}% of total logs)")
#         if failed_logins > 10:
#             root_causes.append(f"Multiple failed login attempts detected: {failed_logins}")
#         if total_query_errors > 5:
#             root_causes.append(f"Query errors detected: {total_query_errors}")
#         if not root_causes:
#             root_causes.append("System healthy - No critical issues detected")

#         # Detect log type
#         detected_type = self.log_type
#         if detected_type == 'auto':
#             # Simple heuristic: check which parser matched most
#             if 'status' in df.columns and len(df[df['status'].notna()]) > len(df) * 0.5:
#                 if 'nginx' in str(df.get('message', '')).lower():
#                     detected_type = 'nginx'
#                 else:
#                     detected_type = 'apache'
#             elif 'mongodb' in str(df.get('message', '')).lower()[:1000]:
#                 detected_type = 'mongodb'
#             elif 'mysql' in str(df.get('message', '')).lower()[:1000]:
#                 detected_type = 'mysql'
#             elif 'postgres' in str(df.get('message', '')).lower()[:1000]:
#                 detected_type = 'postgresql'
#             elif 'redis' in str(df.get('message', '')).lower()[:1000]:
#                 detected_type = 'redis'
#             else:
#                 detected_type = 'generic'

#         return {
#             'success': True,
#             'total_logs': total,
#             'error_count': errors,
#             'warning_count': warnings,
#             'notice_count': notices,
#             'info_count': info,
#             'level_distribution': level_dist,
#             'time_series': time_data,
#             'top_errors': error_list,
#             'status_codes': status_list,
#             'top_ips': ip_list,
#             'log_type': detected_type,
#             'failed_logins': failed_logins,
#             'failed_login_examples': failed_login_examples,
#             'unique_users': unique_users,
#             'active_users_24h': active_users_24h,
#             'top_users': top_users,
#             'total_query_errors': total_query_errors,
#             'root_causes': root_causes
#         }


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/analyze', methods=['POST'])
# def analyze():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file provided'}), 400
        
#         file = request.files['file']
#         log_type = request.form.get('log_type', 'auto')
        
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
        
#         # Save uploaded file
#         filename = file.filename
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Analyze the file
#         analyzer = LogAnalyzer(log_type=log_type)
#         analyzer.analyze_file(filepath)
#         insights = analyzer.generate_insights()
        
#         # Clean up uploaded file
#         try:
#             os.remove(filepath)
#         except:
#             pass
        
#         if insights is None:
#             return jsonify({'error': 'Failed to analyze file'}), 500
        
#         return jsonify(insights)
    
#     except Exception as e:
#         print(f"Error in analyze route: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({'error': str(e)}), 500


# if __name__ == '__main__':
#     print('🚀 Starting Log Analysis Pro...')
#     print('📍 Open your browser and navigate to: http://127.0.0.1:5000')
#     print('📁 Upload your log file to begin analysis')
#     app.run(debug=True, port=5000)


"""
Dynamic Multi-Log Analysis Application - Single File
Complete Grafana-style Dashboard with 8 Log Types

Installation:
    pip install flask pandas openpyxl

Run:
    python app.py
    
Access:
    http://localhost:5000
"""

from flask import Flask, request, jsonify, session, render_template
import pandas as pd
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'ultra-secure-log-analysis-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Enhanced log parsing patterns for maximum accuracy
LOG_PATTERNS = {
    "Apache Logs": {
        "combined": r'(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"',
        "common": r'(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<size>\S+)',
        "error": r'\[(?P<timestamp>[^\]]+)\] \[(?P<level>\w+)\] (?:\[pid (?P<pid>\d+)\])? (?P<message>.*)',
    },
    "Docker Logs": {
        "json": r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) (?P<container_id>\w+) (?P<container_name>[\w\-_]+) (?P<level>\w+) (?P<message>.*)',
        "standard": r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) \[(?P<level>\w+)\] (?P<message>.*)',
        "simple": r'(?P<level>ERROR|WARN|INFO|DEBUG|CRITICAL):\s*(?:\[(?P<container>[\w\-_]+)\])?\s*(?P<message>.*)',
    },
    "Ejabberd Logs": {
        "standard": r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \[(?P<level>\w+)\] (?P<message>.*)',
        "auth": r'.*(?P<event>authentication|login|logout|connection|disconnection).*?(?:user|jid)[:\s]+(?P<user>\S+).*?(?:from\s+(?P<ip>\d+\.\d+\.\d+\.\d+))?',
        "traffic": r'.*(?P<direction>sent|received).*?(?P<bytes>\d+).*?(?:to|from)\s+(?P<target>\S+)',
    },
    "MongoDB Logs": {
        "standard": r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{4}) (?P<level>[IWEF]) (?P<component>\w+)\s+\[(?P<context>[^\]]+)\] (?P<message>.*)',
        "error": r'.*(?P<level>ERROR|WARN).*?(?P<component>\w+).*?(?P<message>.*)',
    },
    "MySQL Logs": {
        "error": r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) (?P<thread>\d+) \[(?P<level>\w+)\] (?P<message>.*)',
        "query": r'(?P<timestamp>\d{6}\s+\d{1,2}:\d{2}:\d{2})\s+(?P<thread>\d+) (?P<command>Query|Connect)\s+(?P<query>.*)',
        "general": r'.*(?P<database>\w+).*?(?P<user>\w+)@(?P<host>\S+).*',
    },
    "Nginx Logs": {
        "access": r'(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"',
        "error": r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<pid>\d+)#(?P<tid>\d+): (?:\*(?P<cid>\d+) )?(?P<message>.*)',
    },
    "PostgreSQL Logs": {
        "standard": r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) (?P<timezone>\w+) \[(?P<pid>\d+)\] (?P<user>\w+)@(?P<database>\w+) (?P<level>\w+):\s+(?P<message>.*)',
        "simple": r'(?P<level>ERROR|WARNING|INFO|LOG|FATAL|PANIC):\s+(?P<message>.*)',
    },
    "Redis Logs": {
        "standard": r'(?P<pid>\d+):(?P<role>\w+) (?P<timestamp>\d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}\.\d+) (?P<level>[*#.-]) (?P<message>.*)',
        "simple": r'(?P<level>ERROR|WARNING|NOTICE).*?(?P<message>.*)',
    }
}

def parse_log_file(content, log_type):
    """Parse log file with enhanced accuracy"""
    lines = content.strip().split('\n')
    parsed_data = []
    patterns = LOG_PATTERNS[log_type]
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        matched = False
        for pattern_name, pattern in patterns.items():
            try:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    data = match.groupdict()
                    data['raw_line'] = line
                    data['line_number'] = line_num
                    
                    if 'level' not in data or not data.get('level'):
                        if 'ERROR' in line.upper() or 'FAIL' in line.upper():
                            data['level'] = 'ERROR'
                        elif 'WARN' in line.upper():
                            data['level'] = 'WARNING'
                        elif 'NOTICE' in line.upper():
                            data['level'] = 'NOTICE'
                        elif 'INFO' in line.upper():
                            data['level'] = 'INFO'
                        elif 'DEBUG' in line.upper():
                            data['level'] = 'DEBUG'
                        else:
                            data['level'] = 'INFO'
                    
                    parsed_data.append(data)
                    matched = True
                    break
            except Exception as e:
                continue
        
        if not matched:
            level = 'INFO'
            if 'ERROR' in line.upper() or 'FAIL' in line.upper():
                level = 'ERROR'
            elif 'WARN' in line.upper():
                level = 'WARNING'
            elif 'CRITICAL' in line.upper():
                level = 'CRITICAL'
            
            parsed_data.append({
                'level': level,
                'message': line,
                'raw_line': line,
                'line_number': line_num
            })
    
    return pd.DataFrame(parsed_data) if parsed_data else pd.DataFrame()

def analyze_apache_logs(df):
    """Comprehensive Apache log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'total_warnings': 0,
        'total_notices': 0,
        'log_level_distribution': {},
        'top_status_messages': [],
        'error_count_over_time': [],
        'status_distribution': {},
        'top_ips': [],
        'top_paths': [],
        'log_levels_over_time': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        level_counts = df['level'].value_counts().to_dict()
        analysis['log_level_distribution'] = {str(k): int(v) for k, v in level_counts.items()}
        
        for level, count in level_counts.items():
            level_str = str(level).upper()
            if 'ERROR' in level_str:
                analysis['total_errors'] += count
            elif 'WARN' in level_str:
                analysis['total_warnings'] += count
            elif 'NOTICE' in level_str:
                analysis['total_notices'] += count
    
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        analysis['status_distribution'] = {str(k): int(v) for k, v in status_counts.items()}
        
        for status in df['status']:
            if str(status).startswith('4') or str(status).startswith('5'):
                analysis['total_errors'] += 1
    
    if 'ip' in df.columns:
        top_ips = df['ip'].value_counts().head(10)
        analysis['top_ips'] = [{'ip': str(k), 'count': int(v)} for k, v in top_ips.items()]
    
    if 'path' in df.columns:
        top_paths = df['path'].value_counts().head(10)
        analysis['top_paths'] = [{'path': str(k), 'count': int(v)} for k, v in top_paths.items()]
    
    if 'message' in df.columns:
        top_msgs = df['message'].value_counts().head(10)
        analysis['top_status_messages'] = [{'message': str(k)[:100], 'count': int(v)} for k, v in top_msgs.items()]
    
    if 'timestamp' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['timestamp'].astype(str).str[:13]
        time_counts = df_time.groupby('hour').size()
        analysis['log_levels_over_time'] = [{'time': str(k), 'count': int(v)} for k, v in time_counts.items()]
        
        error_df = df_time[df_time.get('status', '').astype(str).str.match(r'^[45]\d{2}')]
        if not error_df.empty:
            error_time = error_df.groupby('hour').size()
            analysis['error_count_over_time'] = [{'time': str(k), 'count': int(v)} for k, v in error_time.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_docker_logs(df):
    """Comprehensive Docker log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'log_by_levels': {},
        'top_containers': [],
        'critical_messages': [],
        'error_trends': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        level_counts = df['level'].value_counts()
        analysis['log_by_levels'] = {str(k): int(v) for k, v in level_counts.items()}
        
        for level in df['level']:
            if 'ERROR' in str(level).upper() or 'CRITICAL' in str(level).upper():
                analysis['total_errors'] += 1
    
    container_col = 'container_name' if 'container_name' in df.columns else 'container'
    if container_col in df.columns:
        container_counts = df[container_col].value_counts().head(10)
        analysis['top_containers'] = [{'container': str(k), 'logs': int(v)} for k, v in container_counts.items()]
        
        error_df = df[df.get('level', '').astype(str).str.contains('ERROR|CRITICAL', case=False, na=False)]
        if not error_df.empty and container_col in error_df.columns:
            error_by_container = error_df[container_col].value_counts().head(10)
            analysis['error_trends'] = [{'container': str(k), 'errors': int(v)} for k, v in error_by_container.items()]
    
    if 'message' in df.columns:
        critical_df = df[df.get('level', '').astype(str).str.contains('ERROR|CRITICAL', case=False, na=False)]
        if not critical_df.empty:
            critical_msgs = critical_df['message'].value_counts().head(10)
            analysis['critical_messages'] = [{'message': str(k)[:100], 'count': int(v)} for k, v in critical_msgs.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_ejabberd_logs(df):
    """Comprehensive Ejabberd log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'failed_logins': 0,
        'unique_users': 0,
        'active_users': 0,
        'logs_by_level': {},
        'message_traffic': {'sent': 0, 'received': 0},
        'logs_by_event': {},
        'connections_by_ip': [],
        'logs_over_time': [],
        'failed_auth_users': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        level_counts = df['level'].value_counts()
        analysis['logs_by_level'] = {str(k): int(v) for k, v in level_counts.items()}
        
        for level in df['level']:
            if 'ERROR' in str(level).upper():
                analysis['total_errors'] += 1
    
    if 'user' in df.columns:
        analysis['unique_users'] = df['user'].nunique()
        
        failed_df = df[df.get('message', '').astype(str).str.contains('failed|fail|denied', case=False, na=False)]
        if not failed_df.empty:
            analysis['failed_logins'] = len(failed_df)
            if 'user' in failed_df.columns:
                failed_users = failed_df['user'].value_counts().head(10)
                analysis['failed_auth_users'] = [{'user': str(k), 'attempts': int(v)} for k, v in failed_users.items()]
        
        active_df = df[df.get('message', '').astype(str).str.contains('login|connected', case=False, na=False)]
        analysis['active_users'] = len(active_df)
    
    if 'event' in df.columns:
        event_counts = df['event'].value_counts()
        analysis['logs_by_event'] = {str(k): int(v) for k, v in event_counts.items()}
    
    if 'direction' in df.columns:
        for direction in df['direction']:
            if 'sent' in str(direction).lower():
                analysis['message_traffic']['sent'] += 1
            elif 'received' in str(direction).lower():
                analysis['message_traffic']['received'] += 1
    
    if 'ip' in df.columns:
        ip_counts = df['ip'].value_counts().head(10)
        analysis['connections_by_ip'] = [{'ip': str(k), 'connections': int(v)} for k, v in ip_counts.items()]
    
    if 'timestamp' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['timestamp'].astype(str).str[:13]
        time_counts = df_time.groupby('hour').size()
        analysis['logs_over_time'] = [{'time': str(k), 'count': int(v)} for k, v in time_counts.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_mongodb_logs(df):
    """Comprehensive MongoDB log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'total_warnings': 0,
        'error_rate': 0,
        'top_error_components': [],
        'error_logs_over_time': [],
        'errors_by_context': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        for level in df['level']:
            level_str = str(level).upper()
            if 'E' == level_str or 'ERROR' in level_str:
                analysis['total_errors'] += 1
            elif 'W' == level_str or 'WARN' in level_str:
                analysis['total_warnings'] += 1
    
    if analysis['total_logs'] > 0:
        analysis['error_rate'] = round((analysis['total_errors'] / analysis['total_logs']) * 100, 2)
    
    if 'component' in df.columns:
        error_df = df[df.get('level', '').astype(str).str.contains('E|ERROR', case=False, na=False)]
        if not error_df.empty:
            comp_counts = error_df['component'].value_counts().head(10)
            analysis['top_error_components'] = [{'component': str(k), 'errors': int(v)} for k, v in comp_counts.items()]
    
    if 'context' in df.columns:
        error_df = df[df.get('level', '').astype(str).str.contains('E|ERROR', case=False, na=False)]
        if not error_df.empty:
            context_counts = error_df['context'].value_counts().head(10)
            analysis['errors_by_context'] = [{'context': str(k), 'count': int(v)} for k, v in context_counts.items()]
    
    if 'timestamp' in df.columns:
        error_df = df[df.get('level', '').astype(str).str.contains('E|ERROR', case=False, na=False)].copy()
        if not error_df.empty:
            error_df['hour'] = error_df['timestamp'].astype(str).str[:13]
            error_time = error_df.groupby('hour').size()
            analysis['error_logs_over_time'] = [{'time': str(k), 'count': int(v)} for k, v in error_time.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_mysql_logs(df):
    """Comprehensive MySQL log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_queries': 0,
        'database_usage': [],
        'top_active_users': [],
        'query_volume_over_time': [],
        'query_types': {},
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'query' in df.columns:
        analysis['total_queries'] = df['query'].notna().sum()
        
        for query in df['query'].dropna():
            query_str = str(query).upper()
            if 'SELECT' in query_str:
                analysis['query_types']['SELECT'] = analysis['query_types'].get('SELECT', 0) + 1
            elif 'INSERT' in query_str:
                analysis['query_types']['INSERT'] = analysis['query_types'].get('INSERT', 0) + 1
            elif 'UPDATE' in query_str:
                analysis['query_types']['UPDATE'] = analysis['query_types'].get('UPDATE', 0) + 1
            elif 'DELETE' in query_str:
                analysis['query_types']['DELETE'] = analysis['query_types'].get('DELETE', 0) + 1
    
    if 'database' in df.columns:
        db_counts = df['database'].value_counts().head(10)
        analysis['database_usage'] = [{'database': str(k), 'queries': int(v)} for k, v in db_counts.items()]
    
    if 'user' in df.columns:
        user_counts = df['user'].value_counts().head(10)
        analysis['top_active_users'] = [{'user': str(k), 'queries': int(v)} for k, v in user_counts.items()]
    
    if 'timestamp' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['timestamp'].astype(str).str[:13]
        time_counts = df_time.groupby('hour').size()
        analysis['query_volume_over_time'] = [{'time': str(k), 'volume': int(v)} for k, v in time_counts.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_nginx_logs(df):
    """Comprehensive Nginx log analysis"""
    analysis = {
        'total_requests': len(df),
        'total_errors': 0,
        'avg_response_size': 0,
        'unique_clients': 0,
        'top_browsers': [],
        'error_trend': [],
        'top_urls': [],
        'status_distribution': {},
        'top_client_ips': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        analysis['status_distribution'] = {str(k): int(v) for k, v in status_counts.items()}
        
        for status in df['status']:
            if str(status).startswith('4') or str(status).startswith('5'):
                analysis['total_errors'] += 1
    
    if 'size' in df.columns:
        sizes = pd.to_numeric(df['size'], errors='coerce').dropna()
        if not sizes.empty:
            analysis['avg_response_size'] = int(sizes.mean())
    
    if 'ip' in df.columns:
        analysis['unique_clients'] = df['ip'].nunique()
        
        top_ips = df['ip'].value_counts().head(10)
        analysis['top_client_ips'] = [{'ip': str(k), 'requests': int(v)} for k, v in top_ips.items()]
    
    if 'user_agent' in df.columns:
        browsers = []
        for ua in df['user_agent'].dropna():
            ua_str = str(ua)
            if 'Chrome' in ua_str:
                browsers.append('Chrome')
            elif 'Firefox' in ua_str:
                browsers.append('Firefox')
            elif 'Safari' in ua_str and 'Chrome' not in ua_str:
                browsers.append('Safari')
            elif 'Edge' in ua_str:
                browsers.append('Edge')
            elif 'MSIE' in ua_str or 'Trident' in ua_str:
                browsers.append('Internet Explorer')
            else:
                browsers.append('Other')
        
        if browsers:
            browser_counts = Counter(browsers)
            analysis['top_browsers'] = [{'browser': k, 'count': v} for k, v in browser_counts.most_common(5)]
    
    if 'path' in df.columns:
        url_counts = df['path'].value_counts().head(10)
        analysis['top_urls'] = [{'url': str(k), 'requests': int(v)} for k, v in url_counts.items()]
    
    if 'timestamp' in df.columns:
        error_df = df[df.get('status', '').astype(str).str.match(r'^[45]\d{2}')].copy()
        if not error_df.empty:
            error_df['hour'] = error_df['timestamp'].astype(str).str[:13]
            error_time = error_df.groupby('hour').size()
            analysis['error_trend'] = [{'time': str(k), 'errors': int(v)} for k, v in error_time.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_postgresql_logs(df):
    """Comprehensive PostgreSQL log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'active_databases': 0,
        'unique_users': 0,
        'total_warnings': 0,
        'logs_by_database': [],
        'logs_over_time': [],
        'log_level_distribution': {},
        'top_users_by_activity': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        level_counts = df['level'].value_counts()
        analysis['log_level_distribution'] = {str(k): int(v) for k, v in level_counts.items()}
        
        for level in df['level']:
            level_str = str(level).upper()
            if 'ERROR' in level_str or 'FATAL' in level_str:
                analysis['total_errors'] += 1
            elif 'WARNING' in level_str:
                analysis['total_warnings'] += 1
    
    if 'database' in df.columns:
        analysis['active_databases'] = df['database'].nunique()
        db_counts = df['database'].value_counts().head(10)
        analysis['logs_by_database'] = [{'database': str(k), 'logs': int(v)} for k, v in db_counts.items()]
    
    if 'user' in df.columns:
        analysis['unique_users'] = df['user'].nunique()
        user_counts = df['user'].value_counts().head(10)
        analysis['top_users_by_activity'] = [{'user': str(k), 'queries': int(v)} for k, v in user_counts.items()]
    
    if 'timestamp' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['timestamp'].astype(str).str[:13]
        time_counts = df_time.groupby('hour').size()
        analysis['logs_over_time'] = [{'time': str(k), 'count': int(v)} for k, v in time_counts.items()]
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def analyze_redis_logs(df):
    """Comprehensive Redis log analysis"""
    analysis = {
        'total_logs': len(df),
        'total_errors': 0,
        'total_warnings': 0,
        'error_messages_over_time': [],
        'error_trend': [],
        'logs_trend': [],
        'log_level_distribution': {},
        'top_events': [],
        'table_data': []
    }
    
    if df.empty:
        return analysis
    
    if 'level' in df.columns:
        level_counts = df['level'].value_counts()
        analysis['log_level_distribution'] = {str(k): int(v) for k, v in level_counts.items()}
        
        for level in df['level']:
            level_str = str(level).upper()
            if 'ERROR' in level_str or '#' in str(level):
                analysis['total_errors'] += 1
            elif 'WARNING' in level_str or '-' in str(level):
                analysis['total_warnings'] += 1
    
    if 'message' in df.columns:
        event_counts = df['message'].value_counts().head(10)
        analysis['top_events'] = [{'event': str(k)[:100], 'count': int(v)} for k, v in event_counts.items()]
    
    if 'timestamp' in df.columns:
        df_time = df.copy()
        df_time['hour'] = df_time['timestamp'].astype(str).str[:13]
        
        time_counts = df_time.groupby('hour').size()
        analysis['logs_trend'] = [{'time': str(k), 'count': int(v)} for k, v in time_counts.items()]
        
        error_df = df_time[df_time.get('level', '').astype(str).str.contains('ERROR|#', na=False)]
        if not error_df.empty:
            error_time = error_df.groupby('hour').size()
            analysis['error_trend'] = [{'time': str(k), 'errors': int(v)} for k, v in error_time.items()]
            analysis['error_messages_over_time'] = analysis['error_trend']
    
    analysis['table_data'] = df.head(100).fillna('-').to_dict('records')
    
    return analysis

def read_uploaded_file(file):
    """Read uploaded file with multiple format support"""
    try:
        filename = file.filename
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension in ['txt', 'log']:
            content = file.read().decode('utf-8', errors='ignore')
        elif file_extension == 'csv':
            df = pd.read_csv(file)
            content = '\n'.join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file)
            content = '\n'.join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))
        else:
            content = file.read().decode('utf-8', errors='ignore')
        
        return content
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded log file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        log_type = request.form.get('log_type')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if log_type not in LOG_PATTERNS:
            return jsonify({'error': 'Invalid log type'}), 400
        
        content = read_uploaded_file(file)
        if not content:
            return jsonify({'error': 'Failed to read file'}), 400
        
        df = parse_log_file(content, log_type)
        
        if df.empty:
            return jsonify({'error': 'No logs could be parsed. Please check file format.'}), 400
        
        # Analyze based on log type
        if log_type == 'Apache Logs':
            analysis = analyze_apache_logs(df)
        elif log_type == 'Docker Logs':
            analysis = analyze_docker_logs(df)
        elif log_type == 'Ejabberd Logs':
            analysis = analyze_ejabberd_logs(df)
        elif log_type == 'MongoDB Logs':
            analysis = analyze_mongodb_logs(df)
        elif log_type == 'MySQL Logs':
            analysis = analyze_mysql_logs(df)
        elif log_type == 'Nginx Logs':
            analysis = analyze_nginx_logs(df)
        elif log_type == 'PostgreSQL Logs':
            analysis = analyze_postgresql_logs(df)
        elif log_type == 'Redis Logs':
            analysis = analyze_redis_logs(df)
        else:
            return jsonify({'error': 'Unknown log type'}), 400
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'log_type': log_type
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 ADVANCED MULTI-LOG ANALYSIS DASHBOARD")
    print("="*70)
    print("\n✨ Features:")
    print("   • 8 Log Types: Apache, Docker, Ejabberd, MongoDB, MySQL,")
    print("     Nginx, PostgreSQL, Redis")
    print("   • AI-Powered Pattern Detection")
    print("   • Professional Grafana-Style UI")
    print("   • Interactive Plotly Charts")
    print("   • Real-time Analysis")
    print("\n🌐 Server Info:")
    print("   • URL: http://localhost:5000")
    print("   • Max File Size: 100MB")
    print("   • Formats: .txt, .log, .csv, .xlsx")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
