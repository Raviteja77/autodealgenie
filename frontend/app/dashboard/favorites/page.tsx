"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Box, Container, Typography, Grid, IconButton, Alert, Divider } from "@mui/material";
import {
  Delete as DeleteIcon,
  Speed as SpeedIcon,
  LocalGasStation as LocalGasStationIcon,
  CalendarToday as CalendarTodayIcon,
  DirectionsCar as DirectionsCarIcon,
  LocationOn as LocationOnIcon,
  FavoriteBorder as FavoritesIcon,
} from "@mui/icons-material";
import Link from "next/link";
import { apiClient, Favorite } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useFetchOnce } from "@/lib/hooks";
import { buildVehicleQueryString, ROUTES, NOTIFICATION_DURATION } from "@/lib/constants";
import { getErrorMessage } from "@/lib/utils";
import { Button, Card, LoadingState, ErrorState, EmptyState } from "@/components";

export default function FavoritesPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { executeFetch, shouldFetch } = useFetchOnce();
  
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removeError, setRemoveError] = useState<string | null>(null);

  // Auth check
  useEffect(() => {
    if (!user) {
      router.push(ROUTES.AUTH.LOGIN);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch favorites using custom hook
  useEffect(() => {
    if (!user || !shouldFetch()) return;

    executeFetch(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await apiClient.getFavorites();
        setFavorites(data);
      } catch (err: unknown) {
        console.error("Error fetching favorites:", err);
        setError(getErrorMessage(err));
        throw err;
      } finally {
        setIsLoading(false);
      }
    });
  }, [user, shouldFetch, executeFetch]);

  const handleRemoveFavorite = async (vin: string) => {
    setRemoveError(null);

    // Optimistic update
    const previousFavorites = favorites;
    setFavorites((prev) => prev.filter((fav) => fav.vin !== vin));

    try {
      await apiClient.removeFavorite(vin);
    } catch (err: unknown) {
      console.error("Error removing favorite:", err);
      setFavorites(previousFavorites);
      setRemoveError(getErrorMessage(err));
      setTimeout(() => setRemoveError(null), NOTIFICATION_DURATION.ERROR);
    }
  };

  const handleNavigateToNegotiation = (favorite: Favorite) => {
    const queryString = buildVehicleQueryString({
      ...favorite,
      condition: favorite.condition ?? undefined,
    });
    router.push(`${ROUTES.NEGOTIATION}?${queryString}`);
  };

  const handleNavigateToEvaluation = (favorite: Favorite) => {
    const queryString = buildVehicleQueryString({
      ...favorite,
      condition: favorite.condition ?? undefined,
    });
    router.push(`${ROUTES.EVALUATION}?${queryString}`);
  };

  if (isLoading) {
    return <LoadingState message="Loading your favorites..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Error Loading Favorites"
        message={error}
        showRetry
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          {/* Header */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 4,
              pt: 4,
            }}
          >
            <Box>
              <Typography variant="h3" gutterBottom fontWeight={700}>
                My Favorites
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {favorites.length === 0
                  ? "You haven't added any favorites yet"
                  : `You have ${favorites.length} saved ${
                      favorites.length === 1 ? "vehicle" : "vehicles"
                    }`}
              </Typography>
            </Box>
            <Box sx={{ display: "flex", gap: 2 }}>
              <Link href={ROUTES.SEARCH} style={{ textDecoration: "none" }}>
                <Button variant="outline">Search Cars</Button>
              </Link>
            </Box>
          </Box>

          {/* Remove Error Alert */}
          {removeError && (
            <Alert
              severity="error"
              sx={{ mb: 3 }}
              onClose={() => setRemoveError(null)}
            >
              {removeError}
            </Alert>
          )}

          {/* Empty State */}
          {favorites.length === 0 ? (
            <EmptyState
              icon={<FavoritesIcon />}
              message="No favorites yet"
              description="Start browsing and save your favorite vehicles"
              actionLabel="Browse Cars"
              onAction={() => router.push(ROUTES.SEARCH)}
              minHeight="400px"
            />
          ) : (
            /* Results Grid */
            <Grid container spacing={3}>
              {favorites.map((favorite) => (
                <Grid item xs={12} md={6} lg={4} key={favorite.id}>
                  <Card
                    hover
                    shadow="md"
                    sx={{
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                    }}
                  >
                    {/* Vehicle Image */}
                    <Box
                      sx={{
                        position: "relative",
                        width: "100%",
                        height: 200,
                        bgcolor: "grey.200",
                        backgroundImage: favorite.image
                          ? `url(${favorite.image})`
                          : undefined,
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
                          "&:hover": { bgcolor: "error.light" },
                        }}
                        onClick={() => handleRemoveFavorite(favorite.vin)}
                      >
                        <DeleteIcon color="error" />
                      </IconButton>
                    </Box>

                    <Card.Body sx={{ flexGrow: 1 }}>
                      {/* Vehicle Title */}
                      <Typography variant="h6" gutterBottom fontWeight={600}>
                        {favorite.year} {favorite.make} {favorite.model}
                      </Typography>

                      {/* Price */}
                      <Typography
                        variant="h5"
                        color="primary"
                        gutterBottom
                        fontWeight={700}
                      >
                        ${favorite.price.toLocaleString()}
                      </Typography>

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
                              {favorite.mileage.toLocaleString()} mi
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
                              {favorite.fuel_type || "N/A"}
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
                              {favorite.year}
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
                              {favorite.color || "N/A"}
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* Location */}
                      {favorite.location && (
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
                            {favorite.location}
                          </Typography>
                        </Box>
                      )}

                      {/* Condition */}
                      {favorite.condition && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Condition: {favorite.condition}
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
                          onClick={() => handleNavigateToNegotiation(favorite)}
                        >
                          Negotiate
                        </Button>
                        <Button
                          variant="primary"
                          fullWidth
                          size="sm"
                          onClick={() => handleNavigateToEvaluation(favorite)}
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