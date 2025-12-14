"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  CheckCircle,
  Warning,
  TrendingUp,
  AttachMoney,
  Speed,
  DirectionsCar,
  LocalGasStation,
  ThumbUp,
  ThumbDown,
} from "@mui/icons-material";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import ProgressStepper from "@/components/common/ProgressStepper";

interface VehicleInfo {
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

interface EvaluationScore {
  category: string;
  score: number;
  description: string;
}

export default function EvaluationPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);

  // Mock vehicle data
  const vehicle: VehicleInfo = {
    make: searchParams.get("make") || "Toyota",
    model: searchParams.get("model") || "Camry",
    year: parseInt(searchParams.get("year") || "2022"),
    price: parseInt(searchParams.get("price") || "28500"),
    mileage: parseInt(searchParams.get("mileage") || "15000"),
    fuelType: searchParams.get("fuelType") || "Gasoline",
  };

  // Mock evaluation scores
  const evaluationScores: EvaluationScore[] = [
    {
      category: "Market Value",
      score: 85,
      description: "Price is 8% below market average",
    },
    {
      category: "Vehicle Condition",
      score: 90,
      description: "Excellent condition with low mileage",
    },
    {
      category: "Reliability",
      score: 92,
      description: "High reliability rating for this model",
    },
    {
      category: "Fuel Efficiency",
      score: 78,
      description: "Above average fuel economy",
    },
    {
      category: "Negotiation Success",
      score: 88,
      description: "Secured $3,000 below asking price",
    },
  ];

  const overallScore =
    evaluationScores.reduce((sum, item) => sum + item.score, 0) /
    evaluationScores.length;

  const pros = [
    "Low mileage for the year",
    "Clean vehicle history report",
    "Single owner vehicle",
    "Regular maintenance records available",
    "Price below market average",
  ];

  const cons = [
    "Minor cosmetic wear on interior",
    "Aftermarket stereo system installed",
    "Tires will need replacement within 6 months",
  ];

  const handleFinalize = async () => {
    setLoading(true);
    // In production, save the deal to database
    setTimeout(() => {
      router.push("/deals");
    }, 1500);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    return "error";
  };

  const getOverallRating = (score: number) => {
    if (score >= 85) return { text: "Excellent Deal", icon: <CheckCircle /> };
    if (score >= 70) return { text: "Good Deal", icon: <ThumbUp /> };
    if (score >= 60) return { text: "Fair Deal", icon: <Warning /> };
    return { text: "Reconsider", icon: <ThumbDown /> };
  };

  const rating = getOverallRating(overallScore);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
      <Box sx={{ pt: 10, pb: 4, bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          <ProgressStepper
            activeStep={3}
            steps={["Search", "Results", "Negotiate", "Evaluate", "Finalize"]}
          />

          <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
            Deal Evaluation
          </Typography>

          <Grid container spacing={3}>
            {/* Overall Score Card */}
            <Grid item xs={12}>
              <Card sx={{ bgcolor: "primary.main", color: "white" }}>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      flexWrap: "wrap",
                    }}
                  >
                    <Box>
                      <Typography variant="h5" gutterBottom>
                        Overall Deal Score
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        {rating.icon}
                        <Typography variant="h6">{rating.text}</Typography>
                      </Box>
                    </Box>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="h2" fontWeight="bold">
                        {overallScore.toFixed(0)}
                      </Typography>
                      <Typography variant="body2">out of 100</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Vehicle Details */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Vehicle Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <DirectionsCar sx={{ mr: 2, color: "primary.main" }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Vehicle
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {vehicle.year} {vehicle.make} {vehicle.model}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <AttachMoney sx={{ mr: 2, color: "primary.main" }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Final Price
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          ${vehicle.price.toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Speed sx={{ mr: 2, color: "primary.main" }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Mileage
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {vehicle.mileage.toLocaleString()} miles
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <LocalGasStation sx={{ mr: 2, color: "primary.main" }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Fuel Type
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {vehicle.fuelType}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Detailed Scores */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Detailed Evaluation
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {evaluationScores.map((item, index) => (
                    <Box key={index} sx={{ mb: 3 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium">
                          {item.category}
                        </Typography>
                        <Chip
                          label={item.score}
                          size="small"
                          color={getScoreColor(item.score)}
                        />
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={item.score}
                        color={getScoreColor(item.score)}
                        sx={{ mb: 0.5, height: 8, borderRadius: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {item.description}
                      </Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>

            {/* Pros */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="success.main">
                    Pros
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <List dense>
                    {pros.map((pro, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircle color="success" />
                        </ListItemIcon>
                        <ListItemText primary={pro} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Cons */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="warning.main">
                    Considerations
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <List dense>
                    {cons.map((con, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Warning color="warning" />
                        </ListItemIcon>
                        <ListItemText primary={con} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* AI Recommendation */}
            <Grid item xs={12}>
              <Alert
                severity={overallScore >= 80 ? "success" : "info"}
                icon={<TrendingUp />}
              >
                <Typography variant="body1" fontWeight="medium" gutterBottom>
                  AI Recommendation
                </Typography>
                <Typography variant="body2">
                  {overallScore >= 85
                    ? "This is an excellent deal! The price is competitive, the vehicle is in great condition, and your negotiation was successful. We recommend proceeding with this purchase."
                    : overallScore >= 70
                    ? "This is a good deal overall. The vehicle meets your criteria and the price is fair. Consider the noted considerations before finalizing."
                    : "This deal has some concerns. Review the evaluation carefully and consider if the trade-offs are acceptable for your needs."}
                </Typography>
              </Alert>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: 2,
                }}
              >
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => router.back()}
                >
                  Go Back
                </Button>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <Button
                    variant="outlined"
                    color="error"
                    size="large"
                    onClick={() => router.push("/dashboard/results")}
                  >
                    Reject Deal
                  </Button>
                  <Button
                    variant="contained"
                    size="large"
                    disabled={loading}
                    onClick={handleFinalize}
                  >
                    {loading ? "Finalizing..." : "Accept & Finalize Deal"}
                  </Button>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      <Footer />
    </Box>
  );
}
