"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import { Button, Card, Spinner } from "@/components";
import Chip from "@mui/material/Chip";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import SpeedIcon from "@mui/icons-material/Speed";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import FavoriteIcon from "@mui/icons-material/Favorite";
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder";
import IconButton from "@mui/material/IconButton";
import Link from "next/link";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import ProgressStepper from "@/components/common/ProgressStepper";
import { apiClient, VehicleRecommendation, CarSearchRequest } from "@/lib/api";

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
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchMessage, setSearchMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchVehicles = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Build search request from URL params
        const searchRequest: CarSearchRequest = {};
        
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

        // Call the backend API
        const response = await apiClient.searchCars(searchRequest);
        
        // Transform API response to Vehicle interface
        const transformedVehicles: Vehicle[] = response.top_vehicles.map((v: VehicleRecommendation) => ({
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
          image: v.photo_links && v.photo_links.length > 0 
            ? v.photo_links[0] 
            : `/api/placeholder/400/300?text=${encodeURIComponent((v.make || '') + ' ' + (v.model || ''))}`,
          highlights: v.highlights || [],
          recommendation_score: v.recommendation_score,
          recommendation_summary: v.recommendation_summary,
          dealer_name: v.dealer_name,
          vdp_url: v.vdp_url,
        }));
        
        setVehicles(transformedVehicles);
        setSearchMessage(response.message || null);
      } catch (err: unknown) {
        console.error("Error fetching vehicles:", err);
        const errorMessage = err instanceof Error ? err.message : "Failed to load vehicles. Please try again.";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVehicles();
  }, [searchParams]);

  const toggleFavorite = (vin: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(vin)) {
      newFavorites.delete(vin);
    } else {
      newFavorites.add(vin);
    }
    setFavorites(newFavorites);
  };

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
      <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
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
      <Box sx={{ pt: 10, pb: 4, bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          {/* Header */}
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
            <Box>
            <Typography variant="h3" gutterBottom fontWeight={700}>
              Search Results
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Found {vehicles.length} vehicles matching your criteria
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
              <Button variant="outline">Refine Search</Button>
            </Link>
          </Box>
        </Box>

        {/* AI Message */}
        {searchMessage && (
          <Alert severity="info" sx={{ mb: 3 }}>
            {searchMessage}
          </Alert>
        )}

        {/* Applied Filters */}
        {searchParams.toString() && (
          <Card shadow="sm" sx={{ mb: 3 }}>
            <Card.Body>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Active Filters:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
                {Array.from(searchParams.entries()).map(([key, value]) => (
                  <Chip
                    key={key}
                    label={`${key}: ${value}`}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Stack>
            </Card.Body>
          </Card>
        )}

        {/* Results Grid */}
        {vehicles.length === 0 ? (
          <Card padding="lg">
            <Card.Body>
              <Box sx={{ textAlign: "center", py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No vehicles found matching your criteria
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Try adjusting your filters or search again
                </Typography>
                <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
                  <Button variant="primary">New Search</Button>
                </Link>
              </Box>
            </Card.Body>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {vehicles.map((vehicle) => (
              <Grid item xs={12} md={6} lg={4} key={vehicle.vin || `${vehicle.make}-${vehicle.model}-${vehicle.year}`}>
                <Card hover shadow="md" sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
                  {/* Vehicle Image */}
                  <Box
                    sx={{
                      position: "relative",
                      width: "100%",
                      height: 200,
                      bgcolor: "grey.200",
                      backgroundImage: `url(${vehicle.image})`,
                      backgroundSize: "cover",
                      backgroundPosition: "center",
                    }}
                  >
                    <IconButton
                      sx={{
                        position: "absolute",
                        top: 8,
                        right: 8,
                        bgcolor: "background.paper",
                        "&:hover": { bgcolor: "background.paper" },
                      }}
                      onClick={() => vehicle.vin && toggleFavorite(vehicle.vin)}
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
                        label={`Score: ${vehicle.recommendation_score.toFixed(1)}/10`}
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
                    <Typography variant="h5" color="primary" gutterBottom fontWeight={700}>
                      ${vehicle.price.toLocaleString()}
                    </Typography>

                    {/* Recommendation Summary */}
                    {vehicle.recommendation_summary && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontStyle: "italic" }}>
                        {vehicle.recommendation_summary}
                      </Typography>
                    )}

                    <Divider sx={{ my: 2 }} />

                    {/* Details */}
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                          <SpeedIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {vehicle.mileage.toLocaleString()} mi
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                          <LocalGasStationIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {vehicle.fuelType}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                          <CalendarTodayIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {vehicle.year}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                          <DirectionsCarIcon fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {vehicle.color}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Location */}
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 2 }}>
                      <LocationOnIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {vehicle.location || "Location not specified"}
                      </Typography>
                    </Box>

                    {/* Highlights/Features */}
                    {vehicle.highlights && vehicle.highlights.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                          Highlights:
                        </Typography>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap" sx={{ gap: 0.5 }}>
                          {vehicle.highlights.slice(0, 3).map((highlight: string, index: number) => (
                            <Chip key={index} label={highlight} size="small" variant="outlined" color="primary" />
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
                    <Box sx={{ display: "flex", gap: 1, width: "100%" }}>
                      <Button
                        variant="outline"
                        fullWidth
                        size="sm"
                        onClick={() =>
                          router.push(
                            `/negotiation?vin=${vehicle.vin || ''}&make=${vehicle.make}&model=${vehicle.model}&year=${vehicle.year}&price=${vehicle.price}&mileage=${vehicle.mileage}&fuelType=${vehicle.fuelType || ''}`
                          )
                        }
                      >
                        Negotiate
                      </Button>
                      <Button
                        variant="primary"
                        fullWidth
                        size="sm"
                        onClick={() =>
                          router.push(
                            `/evaluation?vin=${vehicle.vin || ''}&make=${vehicle.make}&model=${vehicle.model}&year=${vehicle.year}&price=${vehicle.price}&mileage=${vehicle.mileage}&fuelType=${vehicle.fuelType || ''}`
                          )
                        }
                      >
                        View Details
                      </Button>
                    </Box>
                  </Card.Footer>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        </Container>
      </Box>
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
