"use client";

import React from "react";
import Link from "next/link";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import { useTheme } from "@mui/material/styles";
import SearchIcon from "@mui/icons-material/Search";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import FavoriteIcon from "@mui/icons-material/Favorite";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import AssessmentIcon from "@mui/icons-material/Assessment";
import HistoryIcon from "@mui/icons-material/History";
import InventoryIcon from "@mui/icons-material/Inventory";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuth } from "@/lib/auth";
import { Button, Footer, Header } from "@/components";

export default function Home() {
  const { user } = useAuth();
  const theme = useTheme();

  const stats = [
    { label: "Active Deals", value: "0", color: theme.palette.primary.main },
    { label: "Saved Searches", value: "0", color: theme.palette.success.main },
    { label: "Favorites", value: "0", color: theme.palette.error.main },
    { label: "Recent Views", value: "0", color: theme.palette.warning.main },
  ];

  const quickActions = [
    {
      title: "Search Cars",
      description: "Find your perfect vehicle with AI-powered search",
      icon: SearchIcon,
      color: "primary",
      href: "/dashboard/search",
    },
    {
      title: "My Deals",
      description: "Manage and track all your automotive deals",
      icon: DirectionsCarIcon,
      color: "warning",
      href: user ? "/deals" : "/auth/login",
    },
    {
      title: "Favorites",
      description: "View your saved vehicles and watchlist",
      icon: FavoriteIcon,
      color: "error",
      href: "/favorites",
    },
  ];

  const features = [
    {
      title: "AI-Powered Recommendations",
      description:
        "Intelligent vehicle suggestions based on preferences and market trends",
      icon: TrendingUpIcon,
    },
    {
      title: "Market Analytics",
      description:
        "Real-time market data and pricing insights for informed decisions",
      icon: AssessmentIcon,
    },
    {
      title: "Deal History",
      description:
        "Track all automotive deals and transactions in one dashboard",
      icon: HistoryIcon,
    },
    {
      title: "Inventory Management",
      description: "Efficient vehicle inventory with automated tracking",
      icon: InventoryIcon,
    },
  ];

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "grey.50" }}>
      {/* Header */}
      <Header />

      <Container maxWidth="lg" sx={{ py: { xs: 6, sm: 8, md: 12 } }}>
        {/* Hero Section */}
        <Box sx={{ textAlign: "center", mb: { xs: 4, md: 6 } }}>
          <Typography
            variant="h2"
            fontWeight={700}
            gutterBottom
            sx={{
              fontSize: { xs: "2.5rem", sm: "3rem", md: "3.75rem" },
              letterSpacing: "-0.02em",
            }}
          >
            Welcome to Auto Deal Genie
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ mb: 4, maxWidth: 600, mx: "auto", fontWeight: 400 }}
          >
            Your AI-powered automotive deal management platform
          </Typography>
          <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
            <Button
              variant="success"
              size="lg"
              startIcon={<SearchIcon />}
              sx={{
                px: 4,
                py: 1.5,
                textTransform: "none",
                fontSize: "1rem",
                fontWeight: 500,
                boxShadow: 1,
                "&:hover": {
                  boxShadow: 2,
                },
              }}
            >
              Start Car Search
            </Button>
          </Link>
        </Box>

        {/* Stats Overview */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: 1,
                  borderColor: "divider",
                  transition: "all 0.2s",
                  "&:hover": {
                    boxShadow: 2,
                    borderColor: "transparent",
                  },
                }}
              >
                <Box
                  sx={{
                    width: 4,
                    height: 48,
                    bgcolor: stat.color,
                    borderRadius: 1,
                    mb: 2,
                  }}
                />
                <Typography variant="h3" fontWeight={700} gutterBottom>
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Quick Actions */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Grid item xs={12} md={4} key={index}>
                <Link href={action.href} style={{ textDecoration: "none" }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      height: "100%",
                      borderRadius: 2,
                      border: 1,
                      borderColor: "divider",
                      cursor: "pointer",
                      transition: "all 0.2s",
                      "&:hover": {
                        boxShadow: 3,
                        borderColor: "transparent",
                        transform: "translateY(-2px)",
                      },
                    }}
                  >
                    <Box
                      sx={{
                        display: "inline-flex",
                        p: 1.5,
                        borderRadius: 1.5,
                        bgcolor: `${action.color}.50`,
                        color: `${action.color}.main`,
                        mb: 2,
                      }}
                    >
                      <Icon sx={{ fontSize: 28 }} />
                    </Box>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      {action.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2 }}
                    >
                      {action.description}
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                      <Typography
                        variant="body2"
                        color="primary"
                        fontWeight={500}
                      >
                        Get started
                      </Typography>
                      <ArrowForwardIcon
                        sx={{ fontSize: 16, color: "primary.main" }}
                      />
                    </Stack>
                  </Paper>
                </Link>
              </Grid>
            );
          })}
        </Grid>

        {/* Features Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight={700} gutterBottom sx={{ mb: 4 }}>
            Platform Features
          </Typography>
          <Grid container spacing={3}>
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Grid item xs={12} md={6} key={index}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 2,
                      border: 1,
                      borderColor: "divider",
                      transition: "all 0.2s",
                      "&:hover": {
                        boxShadow: 2,
                        borderColor: "transparent",
                      },
                    }}
                  >
                    <Stack direction="row" spacing={2} alignItems="flex-start">
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 1.5,
                          bgcolor: "primary.50",
                          color: "primary.main",
                          flexShrink: 0,
                        }}
                      >
                        <Icon sx={{ fontSize: 28 }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {feature.description}
                        </Typography>
                      </Box>
                    </Stack>
                  </Paper>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      </Container>

      {/* Footer */}
      <Footer />
    </Box>
  );
}
