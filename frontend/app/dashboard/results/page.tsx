"use client";

import { useState, useEffect, Suspense, useMemo, useCallback, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import { Button, Card, Spinner } from "@/components";
import Chip from "@mui/material/Chip";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import SpeedIcon from "@mui/icons-material/Speed";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import FavoriteIcon from "@mui/icons-material/Favorite";
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder";
import FilterListIcon from "@mui/icons-material/FilterList";
import BookmarkAddIcon from "@mui/icons-material/BookmarkAdd";
import IconButton from "@mui/material/IconButton";
import Link from "next/link";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import {
  apiClient,
  VehicleRecommendation,
  CarSearchRequest,
  FavoriteCreate,
  SavedSearchCreate,
} from "@/lib/api";
import { useStepper } from "@/app/context";
import { FilterPanel } from "@/components/FilterPanel";
import { SortDropdown, SortOption } from "@/components/SortDropdown";
import { ViewModeToggle } from "@/components/ViewModeToggle";
import { ComparisonBar } from "@/components/ComparisonBar";
import { ComparisonModal } from "@/components/ComparisonModal";
import { SaveSearchModal } from "@/components/SaveSearchModal";
import { SavedSearchesDropdown } from "@/components/SavedSearchesDropdown";
import { LenderRecommendations } from "@/components/LenderRecommendations";
import { useComparison, ComparisonVehicle } from "@/lib/hooks/useComparison";
import { useViewMode } from "@/lib/hooks/useViewMode";
import { useSavedSearches } from "@/lib/hooks/useSavedSearches";

interface Vehicle {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  location?: string;
  color?: string;
  condition?: string;
  image?: string;
  highlights?: string[];
  recommendation_score?: number | null;
  recommendation_summary?: string | null;
  dealer_name?: string | null;
  vdp_url?: string | null;
}

function ResultsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const {
    completeStep,
    setStepData,
    getStepData,
    canNavigateToStep,
    isStepCompleted,
  } = useStepper();

  const hasFetchedRef = useRef(false);
  const currentQueryRef = useRef<string>("");
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New state for enhanced features
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [sortBy, setSortBy] = useState<SortOption>('score_high');
  const [isSaveSearchModalOpen, setIsSaveSearchModalOpen] = useState(false);
  const [showLenderSection, setShowLenderSection] = useState(false);
  
  // Custom hooks
  const comparison = useComparison();
  const { viewMode, setViewMode } = useViewMode('grid');
  const savedSearches = useSavedSearches();

  // Memoize query string for caching
  const currentQueryString = useMemo(
    () => searchParams.toString(),
    [searchParams]
  );

  // Extract financing data from search params
  const loanAmount = useMemo(() => {
    const budgetMax = searchParams.get("budgetMax");
    const downPayment = searchParams.get("downPayment");
    if (budgetMax) {
      const budget = parseFloat(budgetMax);
      const down = downPayment ? parseFloat(downPayment) : 0;
      return budget - down;
    }
    return 0;
  }, [searchParams]);

  const creditScore = useMemo(() => {
    return (searchParams.get("creditScore") || "good") as "excellent" | "good" | "fair" | "poor";
  }, [searchParams]);

  const loanTerm = useMemo(() => {
    const term = searchParams.get("loanTerm");
    return term ? parseInt(term) : 60;
  }, [searchParams]);

  const paymentMethod = useMemo(() => {
    return searchParams.get("paymentMethod") || "cash";
  }, [searchParams]);

  // Show lender section if user is financing
  useEffect(() => {
    setShowLenderSection(paymentMethod === "finance" && loanAmount > 0);
  }, [paymentMethod, loanAmount]);

  /**
   * Check if we should use cached data instead of making a new API call
   */
  const shouldUseCachedData = useCallback(() => {
    const cachedData = getStepData<{
      queryString: string;
      vehicles: Vehicle[];
      message: string | null;
    }>(1);
    return (
      cachedData &&
      cachedData.queryString === currentQueryString &&
      isStepCompleted(1)
    );
  }, [getStepData, currentQueryString, isStepCompleted]);

  useEffect(() => {
    // Prevent duplicate calls for the same query
    if (hasFetchedRef.current && currentQueryRef.current === currentQueryString) {
      return;
    }

    // Check if user can access this step
    if (!canNavigateToStep(1)) {
      router.push("/dashboard/search");
      return;
    }

    const fetchData = async () => {
      // Mark as fetching to prevent duplicate calls
      hasFetchedRef.current = true;
      currentQueryRef.current = currentQueryString;

      try {
        // Check cache first
        if(shouldUseCachedData()) {
          const cachedData = getStepData<{
            queryString: string;
            vehicles: Vehicle[];
            message: string | null;
          }>(1);
  
          if (
            cachedData &&
            cachedData.queryString === currentQueryString &&
            isStepCompleted(1)
          ) {
            // Use cached data
            setVehicles(cachedData.vehicles);
            setSearchMessage(cachedData.message);
            setIsLoading(false);
            
            // Fetch favorites in background (non-blocking)
            fetchFavorites();
            return;
          }
        }

        setIsLoading(true);
        setError(null);

        // Parallel API calls with Promise.allSettled (won't fail if one fails)
        const [vehiclesResult, favoritesResult] = await Promise.allSettled([
          fetchVehiclesData(),
          fetchFavorites(),
        ]);

        // Handle vehicles result
        if (vehiclesResult.status === "fulfilled") {
          const { vehicles: fetchedVehicles, message } = vehiclesResult.value;
          setVehicles(fetchedVehicles);
          setSearchMessage(message);

          // Cache the results
          completeStep(1, {
            queryString: currentQueryString,
            vehicles: fetchedVehicles,
            message: message || null,
          });
        } else {
          const errorMessage =
            vehiclesResult.reason instanceof Error
              ? vehiclesResult.reason.message
              : "Failed to load vehicles. Please try again.";
          setError(errorMessage);
        }

        // Handle favorites result (non-critical, don't show error)
        if (favoritesResult.status === "fulfilled") {
          setFavorites(favoritesResult.value);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to load data. Please try again.";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentQueryString]); // Other dependencies are stable or intentionally excluded

  const fetchVehiclesData = async (): Promise<{
    vehicles: Vehicle[];
    message: string | null;
  }> => {
    console.log("Fetching vehicles from API with params:", searchParams.toString());
    const searchRequest: CarSearchRequest = {};

    // Build search request from URL params
    if (searchParams.get("make")) {
      searchRequest.make = searchParams.get("make")!;
    }
    if (searchParams.get("model")) {
      searchRequest.model = searchParams.get("model")!;
    }
    if (searchParams.get("budgetMin")) {
      searchRequest.budget_min = parseInt(searchParams.get("budgetMin")!);
    }
    if (searchParams.get("budgetMax")) {
      searchRequest.budget_max = parseInt(searchParams.get("budgetMax")!);
    }
    if (searchParams.get("carType")) {
      searchRequest.car_type = searchParams.get("carType")!;
    }
    if (searchParams.get("yearMin")) {
      searchRequest.year_min = parseInt(searchParams.get("yearMin")!);
    }
    if (searchParams.get("yearMax")) {
      searchRequest.year_max = parseInt(searchParams.get("yearMax")!);
    }
    if (searchParams.get("mileageMax")) {
      searchRequest.mileage_max = parseInt(searchParams.get("mileageMax")!);
    }
    if (searchParams.get("userPriorities")) {
      searchRequest.user_priorities = searchParams.get("userPriorities")!;
    }

    const response = await apiClient.searchCars(searchRequest);

    const transformedVehicles: Vehicle[] = response.top_vehicles.map(
      (v: VehicleRecommendation) => ({
        vin: v.vin || undefined,
        make: v.make || "Unknown",
        model: v.model || "Unknown",
        year: v.year || new Date().getFullYear(),
        price: v.price || 0,
        mileage: v.mileage || 0,
        fuelType: v.fuel_type || "Unknown",
        location: v.location || "Unknown",
        color: v.exterior_color || "Unknown",
        condition: v.inventory_type || "Used",
        image:
          v.photo_links && v.photo_links.length > 0
            ? v.photo_links[0]
            : `/api/placeholder/400/300?text=${encodeURIComponent(
                (v.make || "") + " " + (v.model || "")
              )}`,
        highlights: v.highlights || [],
        recommendation_score: v.recommendation_score,
        recommendation_summary: v.recommendation_summary,
        dealer_name: v.dealer_name,
        vdp_url: v.vdp_url,
      })
    );

    return {
      vehicles: transformedVehicles,
      message: response.message || null,
    };
  };

  const fetchFavorites = async (): Promise<Set<string>> => {
    console.log("Fetching favorites from API");
    try {
      const favoritesData = await apiClient.getFavorites();
      const favoriteVins = new Set(favoritesData.map((fav) => fav.vin));
      setFavorites(favoriteVins);
      return favoriteVins;
    } catch (err) {
      console.error("Error fetching favorites:", err);
      // Non-critical error, return empty set
      return new Set();
    }
  };


  const handleVehicleSelection = (vehicle: Vehicle, targetPath: string) => {
    // Store the selected vehicle data for use in subsequent steps
    const existingData = getStepData(1) || {};
    setStepData(1, {
      ...existingData,
      selectedVehicle: vehicle,
    });

    // Navigate to the target page
    const vehicleParams = new URLSearchParams({
      vin: vehicle.vin || "",
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year.toString(),
      price: vehicle.price.toString(),
      mileage: vehicle.mileage.toString(),
      fuelType: vehicle.fuelType || "",
    });
    router.push(`${targetPath}?${vehicleParams.toString()}`);
  };

  const toggleFavorite = async (vehicle: Vehicle) => {
    if (!vehicle.vin) return;

    const vin = vehicle.vin;
    const isFavorited = favorites.has(vin);

    // Optimistic UI update
    const newFavorites = new Set(favorites);
    if (isFavorited) {
      newFavorites.delete(vin);
    } else {
      newFavorites.add(vin);
    }
    setFavorites(newFavorites);

    try {
      if (isFavorited) {
        // Remove from favorites
        await apiClient.removeFavorite(vin);
      } else {
        // Add to favorites
        const favoriteData: FavoriteCreate = {
          vin: vin,
          make: vehicle.make,
          model: vehicle.model,
          year: vehicle.year,
          price: vehicle.price,
          mileage: vehicle.mileage,
          fuel_type: vehicle.fuelType || null,
          location: vehicle.location || null,
          color: vehicle.color || null,
          condition: vehicle.condition || null,
          image: vehicle.image || null,
        };
        await apiClient.addFavorite(favoriteData);
      }
    } catch (err: unknown) {
      console.error("Error toggling favorite:", err);
      // Revert optimistic update on error
      setFavorites(favorites);
      // Optionally show an error message to the user
    }
  };

  // Handler for toggling vehicle comparison
  const handleToggleComparison = (vehicle: Vehicle) => {
    if (!vehicle.vin) return;

    const comparisonVehicle: ComparisonVehicle = {
      vin: vehicle.vin,
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      price: vehicle.price,
      mileage: vehicle.mileage,
      fuelType: vehicle.fuelType,
      condition: vehicle.condition,
      image: vehicle.image,
      highlights: vehicle.highlights,
      recommendation_score: vehicle.recommendation_score,
    };

    comparison.toggleVehicle(comparisonVehicle);
  };

  // Handler for saving search
  const handleSaveSearch = async (search: SavedSearchCreate) => {
    try {
      await savedSearches.createSearch(search);
    } catch (err: unknown) {
      console.error("Error saving search:", err);
      throw err;
    }
  };

  // Handler for deleting saved search
  const handleDeleteSavedSearch = async (searchId: number) => {
    try {
      await savedSearches.deleteSearch(searchId);
    } catch (err: unknown) {
      console.error("Error deleting saved search:", err);
    }
  };

  // Get current search criteria for save modal
  const getCurrentSearchCriteria = (): Partial<SavedSearchCreate> => {
    return {
      make: searchParams.get('make') || undefined,
      model: searchParams.get('model') || undefined,
      budget_min: searchParams.get('budgetMin') ? Number(searchParams.get('budgetMin')) : undefined,
      budget_max: searchParams.get('budgetMax') ? Number(searchParams.get('budgetMax')) : undefined,
      car_type: searchParams.get('carType') || undefined,
      year_min: searchParams.get('yearMin') ? Number(searchParams.get('yearMin')) : undefined,
      year_max: searchParams.get('yearMax') ? Number(searchParams.get('yearMax')) : undefined,
      mileage_max: searchParams.get('mileageMax') ? Number(searchParams.get('mileageMax')) : undefined,
      fuel_type: searchParams.get('fuelType') || undefined,
      transmission: searchParams.get('transmission') || undefined,
      user_priorities: searchParams.get('userPriorities') || undefined,
    };
  };

  // Sort and filter vehicles
  const sortedAndFilteredVehicles = useMemo(() => {
    const filtered = [...vehicles];

    // Apply sorting
    switch (sortBy) {
      case 'price_low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price_high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'mileage_low':
        filtered.sort((a, b) => a.mileage - b.mileage);
        break;
      case 'year_new':
        filtered.sort((a, b) => b.year - a.year);
        break;
      case 'score_high':
        filtered.sort((a, b) => 
          (b.recommendation_score || 0) - (a.recommendation_score || 0)
        );
        break;
      case 'recently_added':
        // Keep original order (assuming it's by recent)
        break;
    }

    return filtered;
  }, [vehicles, sortBy]);

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
        }}
      >
        <Spinner size="lg" text="Finding the best deals for you..." />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
      >
        <Box sx={{ pt: 10, pb: 4, bgcolor: "background.default", flexGrow: 1 }}>
          <Container maxWidth="lg">
            <Alert severity="error" sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Error Loading Vehicles
              </Typography>
              <Typography variant="body2">{error}</Typography>
            </Alert>
            <Box sx={{ textAlign: "center" }}>
              <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
                <Button variant="success">Back to Search</Button>
              </Link>
            </Box>
          </Container>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          {/* Header */}
          {/* <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
            <Box>
            <Typography variant="h3" gutterBottom fontWeight={700}>
              Search Results
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Found {vehicles.length} vehicles matching your criteria
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Link href="/favorites" style={{ textDecoration: "none" }}>
              <Button variant="primary" leftIcon={<FavoriteIcon />}>
                View Favorites
              </Button>
            </Link>
            <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
              <Button variant="outline">Refine Search</Button>
            </Link>
          </Box>
        </Box> */}

          {/* AI Message */}
          {/* {searchMessage && (
            <Alert severity="info" sx={{ mb: 3 }}>
              {searchMessage}
            </Alert>
          )} */}

          {/* Toolbar with controls */}
          <Card shadow="sm" sx={{ mb: 3, mt: 3 }}>
            <Card.Body>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<FilterListIcon />}
                    onClick={() => setIsFilterPanelOpen(true)}
                  >
                    Filters
                  </Button>
                  <SortDropdown value={sortBy} onChange={setSortBy} />
                  <Typography variant="body2" color="text.secondary">
                    {sortedAndFilteredVehicles.length} vehicles
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <SavedSearchesDropdown
                    searches={savedSearches.searches}
                    totalNewMatches={savedSearches.totalNewMatches}
                    onDelete={handleDeleteSavedSearch}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<BookmarkAddIcon />}
                    onClick={() => setIsSaveSearchModalOpen(true)}
                  >
                    Save Search
                  </Button>
                  <ViewModeToggle value={viewMode} onChange={setViewMode} />
                </Box>
              </Box>
            </Card.Body>
          </Card>

          {/* Applied Filters */}
          {searchParams.toString() && (
            <Card shadow="sm" sx={{ mb: 3 }}>
              <Card.Body>
                <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                  Active Filters:
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Stack
                    direction="row"
                    spacing={1}
                    flexWrap="wrap"
                    sx={{ gap: 1 }}
                  >
                    {Array.from(searchParams.entries()).map(([key, value]) => (
                      <Chip
                        key={key}
                        label={`${key}: ${value}`}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                  {/* <Link
                    href="/dashboard/search"
                    style={{ textDecoration: "none" }}
                  >
                    <Button variant="outline">Refine Search</Button>
                  </Link> */}
                </Box>
              </Card.Body>
            </Card>
          )}

          {/* Lender Recommendations Section */}
          {showLenderSection && (
            <Box sx={{ mb: 3 }}>
              <LenderRecommendations
                loanAmount={loanAmount}
                creditScore={creditScore}
                loanTermMonths={loanTerm}
                onLenderSelect={(lender) => {
                  // Store selected lender in stepper context for later use in deal evaluation
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  setStepData(1, (prevStepData: any) => ({
                    ...prevStepData,
                    selectedLender: lender,
                  }));
                }}
                showApplyButton={true}
              />
            </Box>
          )}

          {/* Results Grid */}
          {sortedAndFilteredVehicles.length === 0 ? (
            <Card padding="lg">
              <Card.Body>
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No vehicles found matching your criteria
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 3 }}
                  >
                    Try adjusting your filters or search again
                  </Typography>
                  <Link
                    href="/dashboard/search"
                    style={{ textDecoration: "none" }}
                  >
                    <Button variant="primary">New Search</Button>
                  </Link>
                </Box>
              </Card.Body>
            </Card>
          ) : (
            <Grid container spacing={viewMode === 'list' ? 2 : 3}>
              {sortedAndFilteredVehicles.map((vehicle) => (
                <Grid
                  item
                  xs={12}
                  md={viewMode === 'list' ? 12 : viewMode === 'compact' ? 6 : 6}
                  lg={viewMode === 'list' ? 12 : viewMode === 'compact' ? 6 : 4}
                  key={
                    vehicle.vin ||
                    `${vehicle.make}-${vehicle.model}-${vehicle.year}`
                  }
                >
                  <Card
                    hover
                    shadow="md"
                    sx={{
                      height: "100%",
                      display: "flex",
                      flexDirection: viewMode === 'list' ? 'row' : 'column',
                    }}
                  >
                    {/* Vehicle Image */}
                    <Box
                      sx={{
                        position: "relative",
                        width: viewMode === 'list' ? 300 : '100%',
                        height: viewMode === 'list' ? 'auto' : viewMode === 'compact' ? 150 : 200,
                        bgcolor: "grey.200",
                        backgroundImage: `url(${vehicle.image})`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                        flexShrink: 0,
                      }}
                    >
                      {/* Comparison Checkbox */}
                      {vehicle.vin && (
                        <Box
                          sx={{
                            position: "absolute",
                            top: 8,
                            left: 8,
                            bgcolor: "background.paper",
                            borderRadius: 1,
                            display: 'flex',
                            alignItems: 'center',
                          }}
                        >
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={comparison.isSelected(vehicle.vin)}
                                onChange={() => handleToggleComparison(vehicle)}
                                disabled={!comparison.canAddMore && !comparison.isSelected(vehicle.vin)}
                                size="small"
                              />
                            }
                            label=""
                            sx={{ m: 0, p: 0.5 }}
                          />
                        </Box>
                      )}
                      <IconButton
                        sx={{
                          position: "absolute",
                          top: 8,
                          right: 8,
                          bgcolor: "background.paper",
                          "&:hover": { bgcolor: "background.paper" },
                        }}
                        onClick={() => toggleFavorite(vehicle)}
                      >
                        {vehicle.vin && favorites.has(vehicle.vin) ? (
                          <FavoriteIcon color="error" />
                        ) : (
                          <FavoriteBorderIcon />
                        )}
                      </IconButton>
                      <Chip
                        label={vehicle.condition || "Used"}
                        size="small"
                        color="primary"
                        sx={{ position: "absolute", bottom: 8, left: 8 }}
                      />
                      {vehicle.recommendation_score && (
                        <Chip
                          label={`Score: ${vehicle.recommendation_score.toFixed(
                            1
                          )}/10`}
                          size="small"
                          color="success"
                          sx={{ position: "absolute", top: 8, left: 8 }}
                        />
                      )}
                    </Box>

                    <Card.Body sx={{ flexGrow: 1 }}>
                      {/* Vehicle Title */}
                      <Typography variant="h6" gutterBottom fontWeight={600}>
                        {vehicle.year} {vehicle.make} {vehicle.model}
                      </Typography>

                      {/* Price */}
                      <Typography
                        variant="h5"
                        color="primary"
                        gutterBottom
                        fontWeight={700}
                      >
                        ${vehicle.price.toLocaleString()}
                      </Typography>

                      {/* Recommendation Summary */}
                      {vehicle.recommendation_summary && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 2, fontStyle: "italic" }}
                        >
                          {vehicle.recommendation_summary}
                        </Typography>
                      )}

                      <Divider sx={{ my: 2 }} />

                      {/* Details */}
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <SpeedIcon fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {vehicle.mileage.toLocaleString()} mi
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <LocalGasStationIcon
                              fontSize="small"
                              color="action"
                            />
                            <Typography variant="body2" color="text.secondary">
                              {vehicle.fuelType}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <CalendarTodayIcon
                              fontSize="small"
                              color="action"
                            />
                            <Typography variant="body2" color="text.secondary">
                              {vehicle.year}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <DirectionsCarIcon
                              fontSize="small"
                              color="action"
                            />
                            <Typography variant="body2" color="text.secondary">
                              {vehicle.color}
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* Location */}
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 0.5,
                          mt: 2,
                        }}
                      >
                        <LocationOnIcon fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {vehicle.location || "Location not specified"}
                        </Typography>
                      </Box>

                      {/* Highlights/Features */}
                      {vehicle.highlights && vehicle.highlights.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography
                            variant="subtitle2"
                            gutterBottom
                            fontWeight={600}
                          >
                            Highlights:
                          </Typography>
                          <Stack
                            direction="row"
                            spacing={0.5}
                            flexWrap="wrap"
                            sx={{ gap: 0.5 }}
                          >
                            {vehicle.highlights
                              .slice(0, 3)
                              .map((highlight: string, index: number) => (
                                <Chip
                                  key={index}
                                  label={highlight}
                                  size="small"
                                  variant="outlined"
                                  color="primary"
                                />
                              ))}
                          </Stack>
                        </Box>
                      )}

                      {/* Dealer Info */}
                      {vehicle.dealer_name && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Dealer: {vehicle.dealer_name}
                          </Typography>
                        </Box>
                      )}
                    </Card.Body>

                    <Card.Footer>
                      <Box sx={{ display: "flex", justifyContent: "center", width: "100%" }}>
                        <Button
                          variant="success"
                          fullWidth
                          size="sm"
                          onClick={() =>
                            handleVehicleSelection(
                              vehicle,
                              "/dashboard/negotiation"
                            )
                          }
                        >
                          Negotiate
                        </Button>
                        {/* <Button
                          variant="primary"
                          fullWidth
                          size="sm"
                          onClick={() =>
                            handleVehicleSelection(vehicle, "/evaluation")
                          }
                        >
                          View Details
                        </Button> */}
                      </Box>
                    </Card.Footer>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Container>
      </Box>

      {/* Filter Panel */}
      <FilterPanel
        isOpen={isFilterPanelOpen}
        onClose={() => setIsFilterPanelOpen(false)}
        vehicleCount={sortedAndFilteredVehicles.length}
      />

      {/* Comparison Bar */}
      <ComparisonBar
        selectedVehicles={comparison.selectedVehicles}
        onRemove={comparison.removeVehicle}
        onCompare={comparison.openModal}
        onClear={comparison.clearAll}
        maxCount={comparison.maxCount}
        canCompare={comparison.canCompare}
      />

      {/* Comparison Modal */}
      <ComparisonModal
        isOpen={comparison.isModalOpen}
        onClose={comparison.closeModal}
        vehicles={comparison.selectedVehicles}
      />

      {/* Save Search Modal */}
      <SaveSearchModal
        isOpen={isSaveSearchModalOpen}
        onClose={() => setIsSaveSearchModalOpen(false)}
        onSave={handleSaveSearch}
        currentSearchCriteria={getCurrentSearchCriteria()}
      />
    </Box>
  );
}

export default function DashboardResultsPage() {
  return (
    <Suspense fallback={<Spinner fullScreen text="Loading results..." />}>
      <ResultsContent />
    </Suspense>
  );
}
