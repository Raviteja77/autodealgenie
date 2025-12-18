/**
 * Example page demonstrating mock services usage
 * This page shows how to use the mock API endpoints for development
 */

import { Metadata } from "next";
import { Box, Container, Typography, Alert, Divider } from "@mui/material";
import MarketCheckComponent from "@/components/examples/MarketCheckComponent";
import LLMComponent from "@/components/examples/LLMComponent";

export const metadata: Metadata = {
  title: "Mock Services Examples - AutoDealGenie",
  description: "Examples demonstrating mock API usage for development",
};

export default function ExamplesPage() {
  const useMock = process.env.NEXT_PUBLIC_USE_MOCK === "true";

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Mock Services Examples
        </Typography>

        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body1" gutterBottom>
            This page demonstrates the mock services implementation that allows frontend development
            without relying on live API calls or incurring costs.
          </Typography>
          <Typography variant="body2">
            <strong>Current Mode:</strong> {useMock ? "MOCK" : "REAL"} services
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            To toggle between mock and real services:
            <br />
            • Backend: Set <code>USE_MOCK_SERVICES=true</code> in <code>backend/.env</code>
            <br />
            • Frontend: Set <code>NEXT_PUBLIC_USE_MOCK=true</code> in{" "}
            <code>frontend/.env.local</code>
          </Typography>
        </Alert>

        <Divider sx={{ my: 4 }} />

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" gutterBottom>
            1. Market Check API Example
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            This example demonstrates car search functionality using the mock Market Check API.
            The mock returns realistic vehicle data that matches your search criteria.
          </Typography>
          <MarketCheckComponent />
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" gutterBottom>
            2. LLM API Example
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            This example demonstrates LLM text generation and structured JSON responses using mock
            endpoints. The mock LLM returns context-appropriate responses without actual API calls.
          </Typography>
          <LLMComponent />
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Available Mock Endpoints
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            The following mock endpoints are available when <code>USE_MOCK_SERVICES=true</code>:
          </Typography>

          <Box
            component="ul"
            sx={{
              pl: 3,
              "& li": { mb: 1 },
            }}
          >
            <li>
              <strong>Market Check:</strong> <code>POST /mock/marketcheck/search</code> - Search
              for vehicles
            </li>
            <li>
              <strong>LLM Text:</strong> <code>POST /mock/llm/generate</code> - Generate text
              responses
            </li>
            <li>
              <strong>LLM Structured:</strong> <code>POST /mock/llm/generate-structured</code> -
              Generate structured JSON
            </li>
            <li>
              <strong>Negotiation Create:</strong> <code>POST /mock/negotiation/create</code> -
              Start negotiation session
            </li>
            <li>
              <strong>Negotiation Next:</strong>{" "}
              <code>POST /mock/negotiation/&#123;session_id&#125;/next</code> - Process next round
            </li>
            <li>
              <strong>Negotiation Get:</strong>{" "}
              <code>GET /mock/negotiation/&#123;session_id&#125;</code> - Get session details
            </li>
            <li>
              <strong>Evaluation:</strong> <code>POST /mock/evaluation/evaluate</code> - Evaluate a
              deal
            </li>
            <li>
              <strong>Pipeline Start:</strong> <code>POST /mock/evaluation/pipeline/start</code> -
              Start evaluation pipeline
            </li>
            <li>
              <strong>Pipeline Submit:</strong>{" "}
              <code>POST /mock/evaluation/pipeline/&#123;evaluation_id&#125;/submit</code> - Submit
              answers
            </li>
            <li>
              <strong>Health Check:</strong> <code>GET /mock/marketcheck/health</code> - Service
              health status
            </li>
          </Box>
        </Box>

        <Alert severity="success">
          <Typography variant="body2">
            <strong>Benefits of Mock Services:</strong>
            <br />
            • No external API costs during development
            <br />
            • Faster development without rate limits
            <br />
            • Predictable, consistent test data
            <br />
            • Work offline without external dependencies
            <br />• Easy switching between mock and real services
          </Typography>
        </Alert>
      </Box>
    </Container>
  );
}
