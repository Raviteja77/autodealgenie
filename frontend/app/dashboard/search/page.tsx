"use client";

import { useState, useEffect, useCallback } from "react";
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
  AlertTitle,
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
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from "@mui/icons-material";
import { Input, Button } from "@/components";
import { useAuth } from "@/lib/auth";
import { useStepper } from "@/app/context";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { SearchFormSchema, validateSearchField } from "@/lib/validation/searchFormSchema";
import { useDebounce } from "@/lib/hooks";
import { z } from "zod";

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

function DashboardSearchPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const { completeStep, setStepData } = useStepper();

  const [searchParams, setSearchParams] = useState<SearchFormData>({
    make: "",
    model: "",
    yearMin: 2015,
    yearMax: 2025,
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
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [estimatedPayment, setEstimatedPayment] = useState<number | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  
  // Debounce slider values for performance
  const debouncedBudget = useDebounce(
    { min: searchParams.budgetMin, max: searchParams.budgetMax },
    { delay: 300 }
  );
  const debouncedYear = useDebounce(
    { min: searchParams.yearMin, max: searchParams.yearMax },
    { delay: 300 }
  );

  // Validate on debounced value changes
  useEffect(() => {
    const result = validateSearchField("budgetMax", debouncedBudget.max, {
      budgetMin: debouncedBudget.min,
      budgetMax: debouncedBudget.max,
      paymentMethod: searchParams.paymentMethod,
      downPayment: searchParams.downPayment,
    });
    if (!result.success && result.error) {
      setValidationErrors((prev) => ({ ...prev, budgetMax: result.error! }));
    } else {
      setValidationErrors((prev) => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { budgetMax, ...rest } = prev;
        return rest;
      });
    }
  }, [debouncedBudget, searchParams.paymentMethod, searchParams.downPayment]);

  useEffect(() => {
    const result = validateSearchField("yearMax", debouncedYear.max, {
      yearMin: debouncedYear.min,
      yearMax: debouncedYear.max,
    });
    if (!result.success && result.error) {
      setValidationErrors((prev) => ({ ...prev, yearMax: result.error! }));
    } else {
      setValidationErrors((prev) => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { yearMax, ...rest } = prev;
        return rest;
      });
    }
  }, [debouncedYear]);

  // Validate down payment when budget changes
  useEffect(() => {
    if (searchParams.downPayment !== undefined && searchParams.downPayment > 0) {
      const result = validateSearchField("downPayment", searchParams.downPayment, {
        budgetMax: searchParams.budgetMax,
        downPayment: searchParams.downPayment,
      });
      if (!result.success && result.error) {
        setValidationErrors((prev) => ({ ...prev, downPayment: result.error! }));
      } else {
        setValidationErrors((prev) => {
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          const { downPayment: _, ...rest } = prev;
          return rest;
        });
      }
    }
  }, [searchParams.budgetMax, searchParams.downPayment]);

  // Memoize handlers to prevent unnecessary re-renders
  const handleBudgetChange = useCallback(
    (newValue: number | number[]) => {
      const [min, max] = newValue as number[];
      setSearchParams((prev) => ({
        ...prev,
        budgetMin: min,
        budgetMax: max,
      }));
    },
    []
  );

  const handleYearChange = useCallback(
    (newValue: number | number[]) => {
      const [min, max] = newValue as number[];
      setSearchParams((prev) => ({
        ...prev,
        yearMin: min,
        yearMax: max,
      }));
    },
    []
  );

  const handleMileageChange = useCallback(
    (newValue: number | number[]) => {
      setSearchParams((prev) => ({
        ...prev,
        mileageMax: newValue as number,
      }));
    },
    []
  );

  // Calculate estimated monthly payment
  const calculateMonthlyPayment = (
    price: number,
    downPayment: number,
    term: number,
    creditScore: string
  ) => {
    // Validate inputs to prevent division by zero
    if (term <= 0) {
      return 0;
    }

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

    // Handle edge case where monthly rate is 0
    if (monthlyRate === 0) {
      return Math.round(principal / term);
    }

    const denominator = Math.pow(1 + monthlyRate, term) - 1;
    
    // Additional safety check for division by zero
    if (denominator === 0) {
      return Math.round(principal / term);
    }

    const payment =
      (principal * monthlyRate * Math.pow(1 + monthlyRate, term)) / denominator;

    return Math.round(payment);
  };

  // Auto-update estimated payment when financing parameters change
  useEffect(() => {
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
  }, [
    searchParams.paymentMethod,
    searchParams.downPayment,
    searchParams.loanTerm,
    searchParams.creditScore,
    searchParams.budgetMin,
    searchParams.budgetMax,
  ]);

  const handleSearch = useCallback(() => {
    // Validate the form before search
    try {
      SearchFormSchema.parse(searchParams);
      setValidationErrors({});

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
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors: Record<string, string> = {};
        error.issues.forEach((issue) => {
          if (issue.path[0]) {
            errors[issue.path[0].toString()] = issue.message;
          }
        });
        setValidationErrors(errors);
      }
    }
  }, [searchParams, completeStep, setStepData, router, user]);

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

  const models: Record<string, string[]> = {
    toyota: ["Corolla", "Camry", "Rav4", "Tacoma", "Prius"],
    honda: ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    ford: ["F-150", "Escape", "Explorer", "Mustang", "Focus"],
    chevrolet: ["Silverado", "Equinox", "Malibu", "Tahoe", "Camaro"],
    nissan: ["Altima", "Sentra", "Rogue", "Pathfinder", "Leaf"],
    bmw: ["3 Series", "5 Series", "X3", "X5", "i3"],
    mercedes: ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
    volkswagen: ["Jetta", "Passat", "Tiguan", "Golf", "Atlas"],
    audi: ["A3", "A4", "A6", "Q5", "Q7"],
    hyundai: ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona"],
  };

  const carTypes = [
    "new",
    "used",
    "certified pre-owned",
  ];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Container maxWidth="lg">
        {/* Display validation errors at the top */}
        {Object.keys(validationErrors).length > 0 && (
          <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
            <AlertTitle>Please fix the following errors:</AlertTitle>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {Object.entries(validationErrors).map(([field, error]) => (
                <li key={field}>
                  <strong>{field}:</strong> {error}
                </li>
              ))}
            </ul>
          </Alert>
        )}

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
                      id="budget-slider-label"
                    >
                      ${searchParams.budgetMin.toLocaleString()} - $
                      {searchParams.budgetMax.toLocaleString()}
                    </Typography>
                    <Slider
                      value={[searchParams.budgetMin, searchParams.budgetMax]}
                      onChange={(_, newValue) => handleBudgetChange(newValue)}
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
                      aria-labelledby="budget-slider-label"
                      aria-label="Budget range slider"
                    />
                    {validationErrors.budgetMax && (
                      <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                        {validationErrors.budgetMax}
                      </Typography>
                    )}
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
                              const value = parseInt(e.target.value) || 0;
                              setSearchParams({
                                ...searchParams,
                                downPayment: value,
                              });
                              // Validate down payment
                              const result = validateSearchField(
                                "downPayment",
                                value,
                                { ...searchParams, downPayment: value }
                              );
                              if (!result.success && result.error) {
                                setValidationErrors((prev) => ({
                                  ...prev,
                                  downPayment: result.error!,
                                }));
                              } else {
                                setValidationErrors((prev) => {
                                  // eslint-disable-next-line @typescript-eslint/no-unused-vars
                                  const { downPayment: _, ...rest } = prev;
                                  return rest;
                                });
                              }
                            }}
                            placeholder="e.g., 5000"
                            error={validationErrors.downPayment}
                            aria-label="Down payment amount"
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
                            <InputLabel id="loan-term-label">Loan Term</InputLabel>
                            <Select
                              labelId="loan-term-label"
                              value={searchParams.loanTerm || ""}
                              label="Loan Term"
                              onChange={(e) => {
                                setSearchParams({
                                  ...searchParams,
                                  loanTerm: e.target.value as number,
                                });
                              }}
                              aria-label="Loan term selection"
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
                            <InputLabel id="credit-score-label">Credit Score Range</InputLabel>
                            <Select
                              labelId="credit-score-label"
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
                              }}
                              aria-label="Credit score range selection"
                            >
                              <MenuItem value="excellent">
                                Excellent (750+)
                              </MenuItem>
                              <MenuItem value="good">Good (700-749)</MenuItem>
                              <MenuItem value="fair">Fair (650-699)</MenuItem>
                              <MenuItem value="poor">{"Poor (< 650)"}</MenuItem>
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

                {/* Vehicle Details - Now labeled as Basic Filters */}
                <Grid item xs={12}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <DirectionsCarIcon color="primary" />
                    Basic Vehicle Filters
                  </Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel id="make-label">Make</InputLabel>
                    <Select
                      labelId="make-label"
                      value={searchParams.make}
                      label="Make"
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          make: e.target.value,
                        })
                      }
                      aria-label="Vehicle make selection"
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
                      <InputLabel id="model-label">Model</InputLabel>
                      <Select
                        labelId="model-label"
                        value={searchParams.model}
                        label="Model"
                        onChange={(e) =>
                          setSearchParams({
                            ...searchParams,
                            model: e.target.value,
                          })
                        }
                        aria-label="Vehicle model selection"
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
                    <InputLabel id="car-type-label">Car Type</InputLabel>
                    <Select
                      labelId="car-type-label"
                      value={searchParams.carType}
                      label="Car Type"
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          carType: e.target.value,
                        })
                      }
                      aria-label="Car type selection"
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

                {/* Advanced Filters - Collapsible Section */}
                <Grid item xs={12}>
                  <Box
                    component="button"
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      cursor: "pointer",
                      mt: 2,
                      width: "100%",
                      border: "none",
                      background: "none",
                      padding: 0,
                      textAlign: "left",
                    }}
                    onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setShowAdvancedFilters(!showAdvancedFilters);
                      }
                    }}
                    aria-expanded={showAdvancedFilters}
                    aria-controls="advanced-filters-section"
                  >
                    <Typography
                      variant="h6"
                      sx={{ display: "flex", alignItems: "center", gap: 1, flex: 1 }}
                    >
                      <SpeedIcon color="primary" />
                      Advanced Filters
                    </Typography>
                    <IconButton 
                      aria-label="Toggle advanced filters"
                      aria-expanded={showAdvancedFilters}
                      component="span"
                      tabIndex={-1}
                    >
                      {showAdvancedFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Collapse in={showAdvancedFilters}>
                    <Paper
                      id="advanced-filters-section"
                      variant="outlined"
                      sx={{ p: 3, bgcolor: "grey.50", borderRadius: 2 }}
                      role="region"
                      aria-label="Advanced search filters"
                    >
                      <Grid container spacing={3}>
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
                              id="year-slider-label"
                            >
                              {searchParams.yearMin} - {searchParams.yearMax}
                            </Typography>
                            <Slider
                              value={[searchParams.yearMin, searchParams.yearMax]}
                              onChange={(_, newValue) => handleYearChange(newValue)}
                              valueLabelDisplay="auto"
                              min={2000}
                              max={2025}
                              marks={[
                                { value: 2000, label: "2000" },
                                { value: 2025, label: "2025" },
                              ]}
                              sx={{ color: "success.light" }}
                              aria-labelledby="year-slider-label"
                              aria-label="Year range slider"
                            />
                            {validationErrors.yearMax && (
                              <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                                {validationErrors.yearMax}
                              </Typography>
                            )}
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
                              id="mileage-slider-label"
                            >
                              Up to {searchParams.mileageMax.toLocaleString()} miles
                            </Typography>
                            <Slider
                              value={searchParams.mileageMax}
                              onChange={(_, newValue) => handleMileageChange(newValue)}
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
                              aria-labelledby="mileage-slider-label"
                              aria-label="Maximum mileage slider"
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
                              aria-label="User priorities and preferences"
                            />
                          </Box>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Collapse>
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
                          yearMax: 2025,
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

// Wrap with ErrorBoundary for graceful error handling
export default function DashboardSearchPage() {
  return (
    <ErrorBoundary>
      <DashboardSearchPageContent />
    </ErrorBoundary>
  );
}
