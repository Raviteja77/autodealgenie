"use client";

import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import { Card, Button } from "@/components";
import Link from "next/link";
import SearchIcon from "@mui/icons-material/Search";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import FavoriteIcon from "@mui/icons-material/Favorite";
import HistoryIcon from "@mui/icons-material/History";
import AssessmentIcon from "@mui/icons-material/Assessment";

export default function DashboardPage() {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default", py: 4 }}>
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: "center", mb: 6 }}>
          <Typography variant="h2" gutterBottom fontWeight={700}>
            Welcome to AutoDealGenie
          </Typography>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            Your AI-powered automotive deal management platform
          </Typography>
          <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
            <Button
              variant="primary"
              size="lg"
              leftIcon={<SearchIcon />}
              sx={{ mt: 3 }}
            >
              Start Car Search
            </Button>
          </Link>
        </Box>

        {/* Quick Actions */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          <Grid item xs={12} md={4}>
            <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
              <Card hover shadow="md" sx={{ height: "100%", cursor: "pointer" }}>
                <Card.Body>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: "50%",
                      bgcolor: "primary.light",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mb: 2,
                    }}
                  >
                    <SearchIcon fontSize="large" color="primary" />
                  </Box>
                  <Typography variant="h5" gutterBottom fontWeight={600}>
                    Search Cars
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Find your perfect vehicle with AI-powered search filters
                  </Typography>
                </Card.Body>
              </Card>
            </Link>
          </Grid>

          <Grid item xs={12} md={4}>
            <Link href="/deals" style={{ textDecoration: "none" }}>
              <Card hover shadow="md" sx={{ height: "100%", cursor: "pointer" }}>
                <Card.Body>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: "50%",
                      bgcolor: "success.light",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mb: 2,
                    }}
                  >
                    <DirectionsCarIcon fontSize="large" color="success" />
                  </Box>
                  <Typography variant="h5" gutterBottom fontWeight={600}>
                    My Deals
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Manage and track all your automotive deals in one place
                  </Typography>
                </Card.Body>
              </Card>
            </Link>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card hover shadow="md" sx={{ height: "100%", cursor: "pointer" }}>
              <Card.Body>
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    bgcolor: "error.light",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 2,
                  }}
                >
                  <FavoriteIcon fontSize="large" color="error" />
                </Box>
                <Typography variant="h5" gutterBottom fontWeight={600}>
                  Favorites
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View your saved vehicles and watchlist
                </Typography>
              </Card.Body>
            </Card>
          </Grid>
        </Grid>

        {/* Stats Section */}
        <Card shadow="md" sx={{ mb: 6 }}>
          <Card.Body>
            <Typography variant="h5" gutterBottom fontWeight={600} sx={{ mb: 3 }}>
              Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="h3" color="primary" fontWeight={700}>
                    0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Deals
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="h3" color="success.main" fontWeight={700}>
                    0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Saved Searches
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="h3" color="error.main" fontWeight={700}>
                    0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Favorites
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="h3" color="info.main" fontWeight={700}>
                    0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Recent Views
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Card.Body>
        </Card>

        {/* Features Grid */}
        <Typography variant="h4" gutterBottom fontWeight={700} sx={{ mb: 3 }}>
          Platform Features
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card shadow="sm">
              <Card.Body>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
                  <TrendingUpIcon color="primary" fontSize="large" />
                  <Box>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                      AI-Powered Recommendations
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Get intelligent vehicle recommendations based on your preferences and market trends
                    </Typography>
                  </Box>
                </Box>
              </Card.Body>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card shadow="sm">
              <Card.Body>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
                  <AssessmentIcon color="primary" fontSize="large" />
                  <Box>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                      Market Analytics
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Access real-time market data and pricing insights to make informed decisions
                    </Typography>
                  </Box>
                </Box>
              </Card.Body>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card shadow="sm">
              <Card.Body>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
                  <HistoryIcon color="primary" fontSize="large" />
                  <Box>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                      Deal History
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Track all your automotive deals and transactions in one centralized dashboard
                    </Typography>
                  </Box>
                </Box>
              </Card.Body>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card shadow="sm">
              <Card.Body>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
                  <DirectionsCarIcon color="primary" fontSize="large" />
                  <Box>
                    <Typography variant="h6" gutterBottom fontWeight={600}>
                      Inventory Management
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Efficiently manage vehicle inventory with automated tracking and notifications
                    </Typography>
                  </Box>
                </Box>
              </Card.Body>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
