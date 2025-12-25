"use client";

import { Box, Container, Grid, Typography, Link as MuiLink, IconButton, Divider } from "@mui/material";
import Link from "next/link";
import { GitHub, LinkedIn, Email } from "@mui/icons-material";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <Box
      component="footer"
      sx={{
        bgcolor: "background.paper",
        borderTop: "1px solid",
        borderColor: "divider",
        py: 6,
        mt: "auto",
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              AutoDealGenie
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered automotive deal management platform. Find, negotiate,
              and secure the best car deals with intelligent automation.
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              Quick Links
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              <MuiLink
                component={Link}
                href="/dashboard"
                color="text.secondary"
                underline="hover"
              >
                Dashboard
              </MuiLink>
              <MuiLink
                component={Link}
                href="/dashboard/search"
                color="text.secondary"
                underline="hover"
              >
                Search Cars
              </MuiLink>
              <MuiLink
                component={Link}
                href="/deals"
                color="text.secondary"
                underline="hover"
              >
                My Deals
              </MuiLink>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              Connect With Us
            </Typography>
            <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
              <IconButton
                aria-label="GitHub"
                color="primary"
                href="https://github.com/Raviteja77/autodealgenie"
                target="_blank"
                rel="noopener noreferrer"
              >
                <GitHub />
              </IconButton>
              <IconButton
                aria-label="LinkedIn"
                color="primary"
                href="www.linkedin.com/in/raviteja77"
                target="_blank"
                rel="noopener noreferrer"
              >
                <LinkedIn />
              </IconButton>
              <IconButton
                aria-label="Email"
                color="primary"
                href="mailto:contact@autodealgenie.com"
              >
                <Email />
              </IconButton>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Questions? Email us at{" "}
              <MuiLink href="mailto:contact@autodealgenie.com" underline="hover">
                contact@autodealgenie.com
              </MuiLink>
            </Typography>
          </Grid>
        </Grid>
        <Divider sx={{ my: 3 }} />
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {currentYear} AutoDealGenie. All rights reserved.
          </Typography>
          <Box sx={{ display: "flex", gap: 2 }}>
            <MuiLink
              component={Link}
              href="/privacy"
              color="text.secondary"
              underline="hover"
              variant="body2"
            >
              Privacy Policy
            </MuiLink>
            <MuiLink
              component={Link}
              href="/terms"
              color="text.secondary"
              underline="hover"
              variant="body2"
            >
              Terms of Service
            </MuiLink>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
