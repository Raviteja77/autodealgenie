"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import { Button, Card, Spinner } from "@/components";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import SpeedIcon from "@mui/icons-material/Speed";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import Alert from "@mui/material/Alert";
import Divider from "@mui/material/Divider";
import Link from "next/link";
import { apiClient, Favorite } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function FavoritesPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removeError, setRemoveError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is authenticated
    if (!user) {
      router.push("/auth/login");
      return;
    }

    const fetchFavorites = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await apiClient.getFavorites();
        setFavorites(data);
      } catch (err: unknown) {
        console.error("Error fetching favorites:", err);
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load favorites. Please try again.";
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFavorites();
  }, [user, router]);

  const handleRemoveFavorite = async (vin: string) => {
    setRemoveError(null);
    
    // Optimistic update
    const previousFavorites = favorites;
    setFavorites((prev) => prev.filter((fav) => fav.vin !== vin));
    
    try {
      await apiClient.removeFavorite(vin);
    } catch (err: unknown) {
      console.error("Error removing favorite:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to remove favorite. Please try again.";
      
      // Revert optimistic update
      setFavorites(previousFavorites);
      
      // Show temporary error message without replacing entire page
      setRemoveError(errorMessage);
      setTimeout(() => setRemoveError(null), 5000); // Clear after 5 seconds
    }
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
        <Spinner size="lg" text="Loading your favorites..." />
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
                Error Loading Favorites
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
                  : `You have ${favorites.length} saved ${favorites.length === 1 ? "vehicle" : "vehicles"}`}
              </Typography>
            </Box>
            <Box sx={{ display: "flex", gap: 2 }}>
              <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
                <Button variant="outline">Search Cars</Button>
              </Link>
            </Box>
          </Box>

          {/* Remove Error Alert */}
          {removeError && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setRemoveError(null)}>
              {removeError}
            </Alert>
          )}

          {/* Empty State */}
          {favorites.length === 0 ? (
            <Card padding="lg">
              <Card.Body>
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No favorites yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Start browsing and save your favorite vehicles
                  </Typography>
                  <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
                    <Button variant="primary">Browse Cars</Button>
                  </Link>
                </Box>
              </Card.Body>
            </Card>
          ) : (
            /* Results Grid */
            <Grid container spacing={3}>
              {favorites.map((favorite) => (
                <Grid item xs={12} md={6} lg={4} key={favorite.id}>
                  <Card
                    hover
                    shadow="md"
                    sx={{ height: "100%", display: "flex", flexDirection: "column" }}
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
                      <Typography variant="h5" color="primary" gutterBottom fontWeight={700}>
                        ${favorite.price.toLocaleString()}
                      </Typography>

                      <Divider sx={{ my: 2 }} />

                      {/* Details */}
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <SpeedIcon fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {favorite.mileage.toLocaleString()} mi
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <LocalGasStationIcon fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {favorite.fuel_type || "N/A"}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <CalendarTodayIcon fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {favorite.year}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <DirectionsCarIcon fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {favorite.color || "N/A"}
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* Location */}
                      {favorite.location && (
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 2 }}>
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
                          onClick={() => {
                            const params = new URLSearchParams({
                              vin: favorite.vin,
                              make: favorite.make,
                              model: favorite.model,
                              year: favorite.year.toString(),
                              price: favorite.price.toString(),
                              mileage: favorite.mileage.toString(),
                            });
                            router.push(`/negotiation?${params.toString()}`);
                          }}
                        >
                          Negotiate
                        </Button>
                        <Button
                          variant="primary"
                          fullWidth
                          size="sm"
                          onClick={() => {
                            const params = new URLSearchParams({
                              vin: favorite.vin,
                              make: favorite.make,
                              model: favorite.model,
                              year: favorite.year.toString(),
                              price: favorite.price.toString(),
                              mileage: favorite.mileage.toString(),
                            });
                            router.push(`/evaluation?${params.toString()}`);
                          }}
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
