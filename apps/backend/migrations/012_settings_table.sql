-- Create settings table for application configuration
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for quick lookups
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);

-- Insert default settings
INSERT INTO settings (key, value, category, description) VALUES
    ('active_provider', 'openai', 'model', 'The active model provider'),
    ('model_openai_enabled', 'true', 'model', 'Whether OpenAI provider is enabled'),
    ('model_anthropic_enabled', 'false', 'model', 'Whether Anthropic provider is enabled'),
    ('model_groq_enabled', 'false', 'model', 'Whether Groq provider is enabled'),
    ('model_gemini_enabled', 'false', 'model', 'Whether Gemini provider is enabled'),
    ('model_ollama_enabled', 'false', 'model', 'Whether Ollama provider is enabled')
ON CONFLICT (key) DO NOTHING;