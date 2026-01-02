export interface RawRunRecord {
  timestamp: string;
  persona_id: string;
  question_id: string;
  model_id: string;
  model_family: string;
  api_model_name: string;
  model_version?: string;
  prompt_hash: string;
  system_prompt: string;
  user_message: string;
  full_prompt: string;
  integrity_checks: {
    system_prompt_hash: string;
    system_prompt_valid: boolean;
    question_hash: string;
    question_valid: boolean;
  };
  api_response: {
    id?: string;
    provider?: string;
    model?: string;
    object?: string;
    created?: number;
    choices?: Array<{
      message?: {
        role?: string;
        content?: string;
      };
      finish_reason?: string;
    }>;
    usage?: {
      prompt_tokens?: number;
      completion_tokens?: number;
      total_tokens?: number;
    };
    status_code?: number;
    error?: string | { message?: string; type?: string };
  };
  response_text: string;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  has_error: boolean;
  status_code: number;
  timestamp_start?: string;
  timestamp_end?: string;
  neutrality_analysis: {
    persona_leakage: {
      detected: boolean;
      match_count: number;
      matches: string[][];
    };
    roleplay_adoption: {
      detected: boolean;
      match_count: number;
      matches: string[][];
    };
    refusal_flag: {
      detected: boolean;
      match_count: number;
      matches: string[][];
    };
    harmful_content_flag: {
      detected: boolean;
      match_count: number;
      matches: string[][];
    };
    hedging: {
      count: number;
      frequency: number;
      per_100_words: number;
    };
    certainty: {
      count: number;
      frequency: number;
      per_100_words: number;
    };
    moral_language: {
      count: number;
      frequency: number;
      per_100_words: number;
    };
    prescriptive_verbs: {
      count: number;
      frequency: number;
      per_100_words: number;
    };
  };
}

export interface AnalysisRow {
  timestamp: string;
  persona_id: string;
  question_id: string;
  model_id: string;
  model_family: string;
  api_model_name: string;
  has_error: boolean;
  status_code: number | null;
  response_text_length: number | null;
  persona_leakage_detected: boolean;
  persona_leakage_count: number | null;
  roleplay_adoption_detected: boolean;
  roleplay_adoption_count: number | null;
  refusal_flag_detected: boolean;
  refusal_flag_count: number | null;
  harmful_content_flag_detected: boolean;
  harmful_content_flag_count: number | null;
  hedging_count: number | null;
  hedging_per_100_words: number | null;
  certainty_count: number | null;
  certainty_per_100_words: number | null;
  moral_language_count: number | null;
  moral_language_per_100_words: number | null;
  prescriptive_verbs_count: number | null;
  prescriptive_verbs_per_100_words: number | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
}

export type SortOption = 
  | 'timestamp_desc'
  | 'timestamp_asc'
  | 'persona_id'
  | 'question_id'
  | 'model_id';

export interface FilterState {
  persona_id: string;
  question_id: string;
  model_id: string;
  model_family: string;
  api_model_name: string;
  errorsOnly: boolean;
  search: string;
  sort: SortOption;
}

