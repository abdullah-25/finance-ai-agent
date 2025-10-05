/**
 * Utility functions for parsing backend API responses
 */

export interface BackendResponse {
  response: string | any;
  ok?: boolean;
  is_finance?: boolean;
}

export interface ParsedResponseContent {
  summary_result?: string;
  final_response?: string;
}

/**
 * Converts Python dictionary string format to JSON string format
 * Handles common Python-to-JSON conversions
 */
export function pythonDictToJson(pythonStr: string): string {
  return pythonStr
    .replace(/'/g, '"')           // Replace single quotes with double quotes
    .replace(/True/g, 'true')     // Replace Python True with JSON true
    .replace(/False/g, 'false')   // Replace Python False with JSON false
    .replace(/None/g, 'null');    // Replace Python None with JSON null
}

/**
 * Attempts to parse a Python dictionary string into a JavaScript object
 */
export function parsePythonDict(pythonStr: string): ParsedResponseContent | null {
  try {
    const jsonStr = pythonDictToJson(pythonStr);
    return JSON.parse(jsonStr);
  } catch (error) {
    console.error('Failed to parse Python dict:', error);
    return null;
  }
}

/**
 * Formats the parsed content into a readable message
 */
export function formatResponseContent(content: ParsedResponseContent): string {
  const { summary_result, final_response } = content;
  
  if (summary_result && final_response) {
    return `**Summary:**\n${summary_result}\n\n**Recommendation:**\n${final_response}`;
  } else if (final_response) {
    return final_response;
  } else if (summary_result) {
    return summary_result;
  }
  
  return '';
}

/**
 * Main function to parse backend response and extract AI content
 */
export function parseBackendResponse(data: BackendResponse): string {
  // Check if we have the new response structure with 'ok' field
  if (data.ok !== undefined && data.response) {
    // Handle stringified Python dict in the response field
    if (typeof data.response === 'string') {
      const parsed = parsePythonDict(data.response);
      
      if (parsed) {
        const formatted = formatResponseContent(parsed);
        if (formatted) {
          return formatted;
        }
      }
      
      // If parsing failed or no content found, return the raw response
      return data.response;
    } else if (typeof data.response === 'object') {
      // If response is already an object, extract content directly
      const formatted = formatResponseContent(data.response);
      if (formatted) {
        return formatted;
      }
      
      return data.response.final_response || 
             data.response.summary_result || 
             JSON.stringify(data.response);
    }
  }
  
  // Handle direct structured response (legacy format)
  if (data.summary_result && data.final_response) {
    return formatResponseContent(data as ParsedResponseContent);
  }
  
  // Fallback to original format handling
  return data.response || 
         (data as any).message || 
         (data as any).data || 
         JSON.stringify(data);
}