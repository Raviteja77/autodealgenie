"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButtonGroup,
  ToggleButton,
  Divider,
  Collapse,
  Alert,
  Tooltip,
  IconButton,
} from "@mui/material";
import {
  Search as SearchIcon,
  DirectionsCar as DirectionsCarIcon,
  AttachMoney as AttachMoneyIcon,
  CalendarToday as CalendarTodayIcon,
  Speed as SpeedIcon,
  AccountBalance as AccountBalanceIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";
import { Input, Button } from "@/components";
import { useAuth } from "@/lib/auth";
import { useStepper } from "@/app/context";

interface SearchFormData {
  // Vehicle criteria
  make: string;
  model: string;
  yearMin: number;
  yearMax: number;
  mileageMax: number;
  carType: string;
  fuelType: string;
  transmission: string;
  userPriorities: string;

  // Financing criteria
  paymentMethod: "cash" | "finance" | "both";
  budgetMin: number;
  budgetMax: number;
  downPayment?: number;
  loanTerm?: number; // months
  creditScore?: "excellent" | "good" | "fair" | "poor";
  monthlyPaymentMax?: number;
  tradeInValue?: number;
}

export default function EnhancedSearchPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { completeStep, setStepData } = useStepper();

  const [searchParams, setSearchParams] = useState<SearchFormData>({
    make: "",
    model: "",
    yearMin: 2015,
    yearMax: 2024,
    mileageMax: 100000,
    carType: "",
    fuelType: "",
    transmission: "",
    userPriorities: "",
    paymentMethod: "both",
    budgetMin: 10000,
    budgetMax: 50000,
  });

  const [showFinancingOptions, setShowFinancingOptions] = useState(false);
  const [estimatedPayment, setEstimatedPayment] = useState<number | null>(null);

  // Calculate estimated monthly payment
  const calculateMonthlyPayment = (
    price: number,
    downPayment: number,
    term: number,
    creditScore: string
  ) => {
    // Interest rates based on credit score
    const interestRates = {
      excellent: 0.039, // 3.9%
      good: 0.059, // 5.9%
      fair: 0.089, // 8.9%
      poor: 0.129, // 12.9%
    };

    const rate =
      interestRates[creditScore as keyof typeof interestRates] || 0.059;
    const principal = price - downPayment;
    const monthlyRate = rate / 12;
    const payment =
      (principal * monthlyRate * Math.pow(1 + monthlyRate, term)) /
      (Math.pow(1 + monthlyRate, term) - 1);

    return Math.round(payment);
  };

  // Update estimated payment when financing params change
  const updateEstimatedPayment = () => {
    if (
      searchParams.paymentMethod === "finance" &&
      searchParams.downPayment !== undefined &&
      searchParams.loanTerm &&
      searchParams.creditScore
    ) {
      const avgPrice = (searchParams.budgetMin + searchParams.budgetMax) / 2;
      const payment = calculateMonthlyPayment(
        avgPrice,
        searchParams.downPayment,
        searchParams.loanTerm,
        searchParams.creditScore
      );
      setEstimatedPayment(payment);
    }
  };

  const handleSearch = () => {
    // Convert search params to query string
    const queryParams = new URLSearchParams();

    // Vehicle params
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        queryParams.append(key, value.toString());
      }
    });

    // Mark search step as completed and store search params
    completeStep(0, { searchParams, queryString: queryParams.toString() });
    setStepData(0, { searchParams, queryString: queryParams.toString() });

    // Navigate to results
    if (user) {
      router.push(`/dashboard/results?${queryParams.toString()}`);
    } else {
      router.push(`/auth/login`);
    }
  };

  const makes = [
    "Toyota",
    "Honda",
    "Ford",
    "Chevrolet",
    "Nissan",
    "BMW",
    "Mercedes-Benz",
    "Volkswagen",
    "Audi",
    "Hyundai",
  ];

  const models = {
    toyota: ["Corolla", "Camry", "Rav4", "Tacoma", "Prius"],
    honda: ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    ford: ["F-150", "Escape", "Explorer", "Mustang", "Focus"],
  };

  const carTypes = [
    "Used",
    "New",
    "Certified",
  ];

  const fuelTypes = [
    "Gasoline",
    "Diesel",
    "Electric",
    "Hybrid",
    "Plug-in Hybrid",
  ];

  const transmissions = ["Automatic", "Manual", "CVT"];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Container maxWidth="lg">
        <Grid container spacing={4} sx={{ mt: 1 }}>
          {/* Main Search Form */}
          <Grid item xs={12} md={9}>
            <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
              <Grid container spacing={3}>
                {/* Payment Method Selection */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <AccountBalanceIcon color="primary" />
                    How Will You Pay?
                  </Typography>
                  <ToggleButtonGroup
                    value={searchParams.paymentMethod}
                    exclusive
                    onChange={(_, value) => {
                      if (value !== null) {
                        setSearchParams({
                          ...searchParams,
                          paymentMethod: value,
                        });
                        setShowFinancingOptions(value !== "cash");
                      }
                    }}
                    fullWidth
                    sx={{ mt: 2 }}
                  >
                    <ToggleButton value="cash">
                      <Box sx={{ textAlign: "center", py: 1 }}>
                        <AttachMoneyIcon sx={{ fontSize: 32, mb: 1 }} />
                        <Typography variant="body2">Pay Cash</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Full payment upfront
                        </Typography>
                      </Box>
                    </ToggleButton>
                    <ToggleButton value="finance">
                      <Box sx={{ textAlign: "center", py: 1 }}>
                        <AccountBalanceIcon sx={{ fontSize: 32, mb: 1 }} />
                        <Typography variant="body2">Finance</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Monthly payments
                        </Typography>
                      </Box>
                    </ToggleButton>
                    <ToggleButton value="both">
                      <Box sx={{ textAlign: "center", py: 1 }}>
                        <TrendingUpIcon sx={{ fontSize: 32, mb: 1 }} />
                        <Typography variant="body2">Show Both</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Compare options
                        </Typography>
                      </Box>
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                {/* Budget Section */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <AttachMoneyIcon color="primary" />
                    {searchParams.paymentMethod === "cash"
                      ? "Budget"
                      : searchParams.paymentMethod === "finance"
                      ? "Vehicle Price Range"
                      : "Price Range"}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ px: 2 }}>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      ${searchParams.budgetMin.toLocaleString()} - $
                      {searchParams.budgetMax.toLocaleString()}
                    </Typography>
                    <Slider
                      value={[searchParams.budgetMin, searchParams.budgetMax]}
                      onChange={(_, newValue) => {
                        const [min, max] = newValue as number[];
                        setSearchParams({
                          ...searchParams,
                          budgetMin: min,
                          budgetMax: max,
                        });
                      }}
                      valueLabelDisplay="auto"
                      min={5000}
                      max={100000}
                      step={1000}
                      valueLabelFormat={(value) => `$${value.toLocaleString()}`}
                      marks={[
                        { value: 5000, label: "$5K" },
                        { value: 100000, label: "$100K" },
                      ]}
                      sx={{ color: "success.light" }}
                    />
                  </Box>
                </Grid>

                {/* Financing Options */}
                <Grid item xs={12}>
                  <Collapse in={showFinancingOptions}>
                    <Paper
                      variant="outlined"
                      sx={{ p: 3, bgcolor: "primary.50", borderRadius: 2 }}
                    >
                      <Typography variant="h6" gutterBottom>
                        Financing Details
                        <Tooltip title="Provide financing details to see accurate monthly payment estimates">
                          <IconButton size="small" sx={{ ml: 1 }}>
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Typography>

                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        {/* Down Payment */}
                        <Grid item xs={12} md={6}>
                          <Input
                            fullWidth
                            label="Down Payment"
                            type="number"
                            value={searchParams.downPayment || ""}
                            onChange={(e) => {
                              setSearchParams({
                                ...searchParams,
                                downPayment: parseInt(e.target.value) || 0,
                              });
                              updateEstimatedPayment();
                            }}
                            placeholder="e.g., 5000"
                          />
                        </Grid>

                        {/* Trade-In Value */}
                        <Grid item xs={12} md={6}>
                          <Input
                            fullWidth
                            label="Trade-In Value (Optional)"
                            type="number"
                            value={searchParams.tradeInValue || ""}
                            onChange={(e) =>
                              setSearchParams({
                                ...searchParams,
                                tradeInValue: parseInt(e.target.value) || 0,
                              })
                            }
                            placeholder="e.g., 8000"
                          />
                        </Grid>

                        {/* Loan Term */}
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth>
                            <InputLabel>Loan Term</InputLabel>
                            <Select
                              value={searchParams.loanTerm || ""}
                              label="Loan Term"
                              onChange={(e) => {
                                setSearchParams({
                                  ...searchParams,
                                  loanTerm: e.target.value as number,
                                });
                                updateEstimatedPayment();
                              }}
                            >
                              <MenuItem value={36}>36 months (3 years)</MenuItem>
                              <MenuItem value={48}>48 months (4 years)</MenuItem>
                              <MenuItem value={60}>60 months (5 years)</MenuItem>
                              <MenuItem value={72}>72 months (6 years)</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>

                        {/* Credit Score */}
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth>
                            <InputLabel>Credit Score Range</InputLabel>
                            <Select
                              value={searchParams.creditScore || ""}
                              label="Credit Score Range"
                              onChange={(e) => {
                                setSearchParams({
                                  ...searchParams,
                                  creditScore: e.target.value as
                                    | "excellent"
                                    | "good"
                                    | "fair"
                                    | "poor",
                                });
                                updateEstimatedPayment();
                              }}
                            >
                              <MenuItem value="excellent">
                                Excellent (750+)
                              </MenuItem>
                              <MenuItem value="good">Good (700-749)</MenuItem>
                              <MenuItem value="fair">Fair (650-699)</MenuItem>
                              <MenuItem value="poor">Poor (&lt;650)</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>

                        {/* Maximum Monthly Payment */}
                        <Grid item xs={12}>
                          <Input
                            fullWidth
                            label="Maximum Monthly Payment (Optional)"
                            type="number"
                            value={searchParams.monthlyPaymentMax || ""}
                            onChange={(e) =>
                              setSearchParams({
                                ...searchParams,
                                monthlyPaymentMax:
                                  parseInt(e.target.value) || undefined,
                              })
                            }
                            placeholder="e.g., 500"
                          />
                        </Grid>

                        {/* Estimated Payment Display */}
                        {estimatedPayment && (
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 2 }}>
                              <Typography variant="body2" gutterBottom>
                                <strong>Estimated Monthly Payment:</strong>
                              </Typography>
                              <Typography variant="h5" color="primary">
                                ${estimatedPayment}/month
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Based on average price in your range. Actual
                                rates may vary.
                              </Typography>
                            </Alert>
                          </Grid>
                        )}
                      </Grid>
                    </Paper>
                  </Collapse>
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                {/* Vehicle Details */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <DirectionsCarIcon color="primary" />
                    Vehicle Filters
                  </Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Make</InputLabel>
                    <Select
                      value={searchParams.make}
                      label="Make"
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          make: e.target.value,
                        })
                      }
                    >
                      <MenuItem value="">Any</MenuItem>
                      {makes.map((type) => (
                        <MenuItem key={type} value={type.toLowerCase()}>
                          {type}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {searchParams.make && (
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Model</InputLabel>
                      <Select
                        value={searchParams.model}
                        label="Model"
                        onChange={(e) =>
                          setSearchParams({
                            ...searchParams,
                            model: e.target.value,
                          })
                        }
                      >
                        <MenuItem value="">Any</MenuItem>
                        {models[
                          searchParams.make as keyof typeof models
                        ]?.map((model) => (
                          <MenuItem key={model} value={model.toLowerCase()}>
                            {model}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                )}

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Car Type</InputLabel>
                    <Select
                      value={searchParams.carType}
                      label="Car Type"
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          carType: e.target.value,
                        })
                      }
                    >
                      <MenuItem value="">Any</MenuItem>
                      {carTypes.map((type) => (
                        <MenuItem key={type} value={type.toLowerCase()}>
                          {type}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Year Range */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mt: 2,
                    }}
                  >
                    <CalendarTodayIcon color="primary" />
                    Year Range
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ px: 2 }}>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      {searchParams.yearMin} - {searchParams.yearMax}
                    </Typography>
                    <Slider
                      value={[searchParams.yearMin, searchParams.yearMax]}
                      onChange={(_, newValue) => {
                        const [min, max] = newValue as number[];
                        setSearchParams({
                          ...searchParams,
                          yearMin: min,
                          yearMax: max,
                        });
                      }}
                      valueLabelDisplay="auto"
                      min={2000}
                      max={2024}
                      marks={[
                        { value: 2000, label: "2000" },
                        { value: 2024, label: "2024" },
                      ]}
                      sx={{ color: "success.light" }}
                    />
                  </Box>
                </Grid>

                {/* Mileage */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mt: 2,
                    }}
                  >
                    <SpeedIcon color="primary" />
                    Maximum Mileage
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ px: 2 }}>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Up to {searchParams.mileageMax.toLocaleString()} miles
                    </Typography>
                    <Slider
                      value={searchParams.mileageMax}
                      onChange={(_, newValue) =>
                        setSearchParams({
                          ...searchParams,
                          mileageMax: newValue as number,
                        })
                      }
                      valueLabelDisplay="auto"
                      min={10000}
                      max={200000}
                      step={5000}
                      valueLabelFormat={(value) =>
                        `${value.toLocaleString()} mi`
                      }
                      marks={[
                        { value: 10000, label: "10K" },
                        { value: 200000, label: "200K" },
                      ]}
                      sx={{ color: "success.light" }}
                    />
                  </Box>
                </Grid>

                {/* Additional Preferences */}
                <Grid item xs={12}>
                  <Box sx={{ px: 2 }}>
                    <Input
                      multiLine={true}
                      fullWidth
                      label="Your Priorities (Optional)"
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          userPriorities: e.target.value,
                        })
                      }
                      placeholder="e.g., fuel efficiency, safety features, low maintenance costs"
                      value={searchParams.userPriorities}
                    />
                  </Box>
                </Grid>

                {/* Search Button */}
                <Grid item xs={12}>
                  <Box
                    sx={{
                      display: "flex",
                      gap: 2,
                      justifyContent: "flex-end",
                      mt: 3,
                    }}
                  >
                    <Button
                      variant="outline"
                      onClick={() =>
                        setSearchParams({
                          make: "",
                          model: "",
                          yearMin: 2015,
                          yearMax: 2024,
                          mileageMax: 100000,
                          carType: "",
                          fuelType: "",
                          transmission: "",
                          userPriorities: "",
                          paymentMethod: "both",
                          budgetMin: 10000,
                          budgetMax: 50000,
                        })
                      }
                    >
                      Reset
                    </Button>
                    <Button
                      variant="success"
                      size="lg"
                      leftIcon={<SearchIcon />}
                      onClick={handleSearch}
                    >
                      Search Cars
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={3}>
            {/* Quick Tips */}
            <Box sx={{ position: "sticky", top: 100 }}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  💡 Financing Tips
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • 20% down payment typically gets better rates
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • Shorter loans save on total interest
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • Check your credit score before applying
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Get pre-approved for better negotiation power
                </Typography>
              </Paper>

              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Pro Tip:</strong> Knowing your financing options
                  before shopping gives you better negotiating power with
                  dealers.
                </Typography>
              </Alert>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
