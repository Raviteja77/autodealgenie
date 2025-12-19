/**
 * Example component demonstrating mock LLM API usage
 * Shows how to generate text and structured JSON using either real or mock backend
 */

"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { Button, Card } from "../ui";

interface LLMResponse {
  content: string | Record<string, any>;
  prompt_id: string;
  model: string;
  tokens_used?: number;
}

function LLMComponent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LLMResponse | null>(null);
  const [promptType, setPromptType] = useState<string>("negotiation");
  const [variables, setVariables] = useState<Record<string, any>>({
    round_number: 1,
    asking_price: 30000,
    counter_offer: 28000,
  });

  const handleGenerate = async (structured: boolean = false) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const endpoint = structured
        ? "/mock/llm/generate-structured"
        : "/mock/llm/generate";

      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          prompt_id: promptType,
          variables: variables,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate LLM response");
    } finally {
      setLoading(false);
    }
  };

  const handleVariableChange = (key: string, value: any) => {
    setVariables({ ...variables, [key]: value });
  };

  const useMock = process.env.NEXT_PUBLIC_USE_MOCK === "true";

  return (
    <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
      <Typography variant="h4" gutterBottom>
        LLM API Example
      </Typography>

      <Alert severity={useMock ? "info" : "success"} sx={{ mb: 3 }}>
        {useMock
          ? "Using MOCK backend - enable with NEXT_PUBLIC_USE_MOCK=true"
          : "Using REAL backend - disable mocks with NEXT_PUBLIC_USE_MOCK=false"}
      </Alert>

      <Card sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          LLM Parameters
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>Prompt Type</InputLabel>
            <Select
              value={promptType}
              label="Prompt Type"
              onChange={(e) => setPromptType(e.target.value)}
            >
              <MenuItem value="negotiation">Negotiation</MenuItem>
              <MenuItem value="evaluation">Evaluation</MenuItem>
              <MenuItem value="recommendation">Recommendation</MenuItem>
              <MenuItem value="selection">Selection</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="subtitle2" color="text.secondary">
            Variables (JSON):
          </Typography>

          <TextField
            multiline
            rows={6}
            fullWidth
            value={JSON.stringify(variables, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setVariables(parsed);
              } catch {
                // Ignore parse errors while typing
              }
            }}
            placeholder='{"key": "value"}'
            variant="outlined"
          />

          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              onClick={() => handleGenerate(false)}
              disabled={loading}
              variant="primary"
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : "Generate Text"}
            </Button>

            <Button
              onClick={() => handleGenerate(true)}
              disabled={loading}
              variant="secondary"
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : "Generate Structured JSON"}
            </Button>
          </Box>
        </Box>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Card sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            LLM Response
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Model: {result.model}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Prompt ID: {result.prompt_id}
            </Typography>
            {result.tokens_used && (
              <Typography variant="body2" color="text.secondary">
                Tokens Used: {result.tokens_used}
              </Typography>
            )}
          </Box>

          <Card variant="outlined" sx={{ p: 2, bgcolor: "grey.50" }}>
            <Typography variant="subtitle2" gutterBottom>
              Content:
            </Typography>
            {typeof result.content === "string" ? (
              <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                {result.content}
              </Typography>
            ) : (
              <Box
                component="pre"
                sx={{
                  p: 2,
                  bgcolor: "grey.100",
                  borderRadius: 1,
                  overflow: "auto",
                  fontSize: "0.875rem",
                }}
              >
                {JSON.stringify(result.content, null, 2)}
              </Box>
            )}
          </Card>
        </Card>
      )}
    </Box>
  );
}

export default LLMComponent;