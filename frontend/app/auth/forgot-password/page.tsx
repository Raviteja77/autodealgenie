"use client";

import { useState } from "react";
import {
  Box,
  Container,
  Paper,
  TextField,
  Typography,
  Link as MuiLink,
  Alert,
  InputAdornment,
} from "@mui/material";
import { Email, ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { Button } from "@/components";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);
    setLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/v1/auth/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Extract the error message from the detail array, if available
        const errorMessage = data.detail?.[0]?.msg || "Failed to request password reset";
        throw new Error(errorMessage);
      }

      setSuccess(true);
      setEmail("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to request password reset. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        bgcolor: "background.default",
        py: 8,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            pt: 3,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            Forgot Password?
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 3, textAlign: "center" }}
          >
            Enter your email address and we&apos;ll send you a link to reset
            your password.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ width: "100%", mb: 2 }}>
              If your email is registered, you will receive a password reset
              link shortly. Please check your inbox.
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading || success}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="primary"
              disabled={loading || success}
              isLoading={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              Send Reset Link
            </Button>
            <Box sx={{ textAlign: "center" }}>
              <MuiLink
                component={Link}
                href="/auth/login"
                variant="body2"
                sx={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 0.5,
                }}
              >
                <ArrowBack fontSize="small" />
                Back to Login
              </MuiLink>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
