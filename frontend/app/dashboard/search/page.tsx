"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Container,
  Grid,
  Paper,
  Divider,
  Collapse,
  Alert,
  AlertTitle,
  IconButton,
  Typography,
} from "@mui/material";
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Speed as SpeedIcon,
} from "@mui/icons-material";
import { Button } from "@/components";
import { useAuth } from "@/lib/auth";
import { useStepper } from "@/app/context";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { SearchFormSchema, validateSearchField } from "@/lib/validation/searchFormSchema";
import { useDebounce } from "@/lib/hooks";
import { z } from "zod";
import {
  PaymentMethodSelector,
  BudgetRangeSlider,
  FinancingOptionsForm,
  BasicVehicleFilters,
  AdvancedFilters,
  SearchSidebar,
} from "./components";

interface SearchFormData {
  // Vehicle criteria
  make: string;
  model: string;
  yearMin: number;
  yearMax: number;
  mileageMax: number;
  carType: string;
  bodyType: string;
  fuelType: string;
  transmission: string;
  drivetrain: string;
  mustHaveFeatures: string[];
  userPriorities: string;

  // Financing criteria
  paymentMethod: "cash" | "finance" | "both";
  budgetMin: number;
  budgetMax: number;
  downPayment?: number;
  loanTerm?: number;
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
    bodyType: "",
    fuelType: "",
    transmission: "",
    drivetrain: "",
    mustHaveFeatures: [],
    userPriorities: "",
    paymentMethod: "cash",
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
      ...searchParams,
      budgetMin: debouncedBudget.min,
      budgetMax: debouncedBudget.max,
      paymentMethod: searchParams.paymentMethod,
      downPayment: searchParams.downPayment,
    });
    if (!result.success && result.error) {
      setValidationErrors((prev) => ({ ...prev, budgetMax: result.error! }));
    } else {
      setValidationErrors((prev) => {
        const { budgetMax, ...rest } = prev;
        return rest;
      });
    }
  }, [debouncedBudget, searchParams.paymentMethod, searchParams.downPayment]);

  useEffect(() => {
    const result = validateSearchField("yearMax", debouncedYear.max, {
      ...searchParams, // Include all existing search params
      yearMin: debouncedYear.min,
      yearMax: debouncedYear.max,
    });
    if (!result.success && result.error) {
      setValidationErrors((prev) => ({ ...prev, yearMax: result.error! }));
    } else {
      setValidationErrors((prev) => {
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

  // Data for dropdowns
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

  const carTypes = ["New", "Used", "Certified Pre-Owned"];

  const bodyTypes = [
    "Sedan",
    "SUV",
    "Truck",
    "Coupe",
    "Wagon",
    "Van",
    "Convertible",
    "Hatchback",
  ];

  const fuelTypes = [
    "Gasoline",
    "Diesel",
    "Electric",
    "Hybrid",
    "Plug-in Hybrid",
  ];

  const transmissions = ["Automatic", "Manual", "CVT"];

  const drivetrains = ["FWD", "RWD", "AWD", "4WD"];

  const featureOptions = [
    "Backup Camera",
    "Bluetooth",
    "Navigation",
    "Sunroof",
    "Leather Seats",
    "Heated Seats",
    "Apple CarPlay",
    "Android Auto",
    "Adaptive Cruise Control",
    "Lane Keep Assist",
    "Blind Spot Monitor",
    "Parking Sensors",
  ];

  // Conditional filter logic: hide year and mileage for new cars
  const normalizedCarType = (searchParams.carType || "").trim().toLowerCase();
  const isNewCar = normalizedCarType === "new";
  const showYearFilter = !isNewCar;
  const showMileageFilter = !isNewCar;

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
                  <PaymentMethodSelector
                    value={searchParams.paymentMethod}
                    onChange={(value) => {
                      setSearchParams({
                        ...searchParams,
                        paymentMethod: value,
                      });
                      setShowFinancingOptions(value !== "cash");
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                {/* Budget Section */}
                <Grid item xs={12}>
                  <BudgetRangeSlider
                    min={searchParams.budgetMin}
                    max={searchParams.budgetMax}
                    onChange={(min, max) => {
                      setSearchParams((prev) => ({
                        ...prev,
                        budgetMin: min,
                        budgetMax: max,
                      }));
                    }}
                    paymentMethod={searchParams.paymentMethod}
                    error={validationErrors.budgetMax}
                  />
                </Grid>

                {/* Financing Options */}
                <Grid item xs={12}>
                  <Collapse in={showFinancingOptions}>
                    <FinancingOptionsForm
                      downPayment={searchParams.downPayment}
                      tradeInValue={searchParams.tradeInValue}
                      loanTerm={searchParams.loanTerm}
                      creditScore={searchParams.creditScore}
                      monthlyPaymentMax={searchParams.monthlyPaymentMax}
                      estimatedPayment={estimatedPayment}
                      onDownPaymentChange={(value) => {
                        setSearchParams((prev) => ({
                          ...prev,
                          downPayment: value,
                        }));
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
                      onTradeInValueChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          tradeInValue: value,
                        }))
                      }
                      onLoanTermChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          loanTerm: value,
                        }))
                      }
                      onCreditScoreChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          creditScore: value,
                        }))
                      }
                      onMonthlyPaymentMaxChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          monthlyPaymentMax: value,
                        }))
                      }
                      downPaymentError={validationErrors.downPayment}
                    />
                  </Collapse>
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                {/* Basic Vehicle Filters */}
                <BasicVehicleFilters
                  make={searchParams.make}
                  model={searchParams.model}
                  carType={searchParams.carType}
                  bodyType={searchParams.bodyType}
                  onMakeChange={(value) =>
                    setSearchParams((prev) => ({
                      ...prev,
                      make: value,
                      model: "", // Reset model when make changes
                    }))
                  }
                  onModelChange={(value) =>
                    setSearchParams((prev) => ({ ...prev, model: value }))
                  }
                  onCarTypeChange={(value) =>
                    setSearchParams((prev) => ({ ...prev, carType: value }))
                  }
                  onBodyTypeChange={(value) =>
                    setSearchParams((prev) => ({ ...prev, bodyType: value }))
                  }
                  makes={makes}
                  models={models}
                  carTypes={carTypes}
                  bodyTypes={bodyTypes}
                />

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
                    <AdvancedFilters
                      yearMin={searchParams.yearMin}
                      yearMax={searchParams.yearMax}
                      mileageMax={searchParams.mileageMax}
                      fuelType={searchParams.fuelType}
                      transmission={searchParams.transmission}
                      drivetrain={searchParams.drivetrain}
                      mustHaveFeatures={searchParams.mustHaveFeatures}
                      userPriorities={searchParams.userPriorities}
                      showYearFilter={showYearFilter}
                      showMileageFilter={showMileageFilter}
                      onYearChange={(min, max) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          yearMin: min,
                          yearMax: max,
                        }))
                      }
                      onMileageChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          mileageMax: value,
                        }))
                      }
                      onFuelTypeChange={(value) =>
                        setSearchParams((prev) => ({ ...prev, fuelType: value }))
                      }
                      onTransmissionChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          transmission: value,
                        }))
                      }
                      onDrivetrainChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          drivetrain: value,
                        }))
                      }
                      onMustHaveFeaturesChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          mustHaveFeatures: value,
                        }))
                      }
                      onUserPrioritiesChange={(value) =>
                        setSearchParams((prev) => ({
                          ...prev,
                          userPriorities: value,
                        }))
                      }
                      yearError={validationErrors.yearMax}
                      fuelTypes={fuelTypes}
                      transmissions={transmissions}
                      drivetrains={drivetrains}
                      featureOptions={featureOptions}
                    />
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
                          bodyType: "",
                          fuelType: "",
                          transmission: "",
                          drivetrain: "",
                          mustHaveFeatures: [],
                          userPriorities: "",
                          paymentMethod: "cash",
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
            <SearchSidebar />
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
