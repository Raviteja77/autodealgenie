"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
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

// Mock data generator
const generateMockVehicles = (count: number = 12) => {
  const makes = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz", "Audi", "Nissan"];
  const models: Record<string, string[]> = {
    Toyota: ["Camry", "Corolla", "RAV4", "Highlander"],
    Honda: ["Accord", "Civic", "CR-V", "Pilot"],
    Ford: ["F-150", "Mustang", "Explorer", "Escape"],
    Chevrolet: ["Silverado", "Equinox", "Malibu", "Tahoe"],
    BMW: ["3 Series", "5 Series", "X3", "X5"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE"],
    Audi: ["A4", "A6", "Q5", "Q7"],
    Nissan: ["Altima", "Rogue", "Sentra", "Pathfinder"],
  };
  const fuelTypes = ["Gasoline", "Diesel", "Hybrid", "Electric"];
  const locations = ["Los Angeles, CA", "New York, NY", "Chicago, IL", "Houston, TX", "Phoenix, AZ"];
  const colors = ["Black", "White", "Silver", "Blue", "Red", "Gray"];

  return Array.from({ length: count }, (_, i) => {
    const make = makes[Math.floor(Math.random() * makes.length)];
    const model = models[make][Math.floor(Math.random() * models[make].length)];
    const year = 2018 + Math.floor(Math.random() * 7);
    const price = 15000 + Math.floor(Math.random() * 40000);
    const mileage = 10000 + Math.floor(Math.random() * 90000);
    
    return {
      id: i + 1,
      make,
      model,
      year,
      price,
      mileage,
      fuelType: fuelTypes[Math.floor(Math.random() * fuelTypes.length)],
      location: locations[Math.floor(Math.random() * locations.length)],
      color: colors[Math.floor(Math.random() * colors.length)],
      condition: Math.random() > 0.5 ? "Certified Pre-Owned" : "Used",
      image: `https://via.placeholder.com/400x300/2563eb/ffffff?text=${make}+${model}`,
      features: ["Backup Camera", "Bluetooth", "Cruise Control", "Power Windows"]
        .filter(() => Math.random() > 0.5),
    };
  });
};

interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  location: string;
  color: string;
  condition: string;
  image: string;
  features: string[];
}

function ResultsContent() {
  const searchParams = useSearchParams();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [favorites, setFavorites] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setIsLoading(true);
    setTimeout(() => {
      const mockData = generateMockVehicles();
      // Filter based on search params (simplified)
      const filtered = mockData.filter(vehicle => {
        const make = searchParams.get("make");
        if (make && !vehicle.make.toLowerCase().includes(make.toLowerCase())) {
          return false;
        }
        return true;
      });
      setVehicles(filtered);
      setIsLoading(false);
    }, 1000);
  }, [searchParams]);

  const toggleFavorite = (id: number) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(id)) {
      newFavorites.delete(id);
    } else {
      newFavorites.add(id);
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

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default", py: 4 }}>
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
              <Grid item xs={12} md={6} lg={4} key={vehicle.id}>
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
                      onClick={() => toggleFavorite(vehicle.id)}
                    >
                      {favorites.has(vehicle.id) ? (
                        <FavoriteIcon color="error" />
                      ) : (
                        <FavoriteBorderIcon />
                      )}
                    </IconButton>
                    <Chip
                      label={vehicle.condition}
                      size="small"
                      color="primary"
                      sx={{ position: "absolute", bottom: 8, left: 8 }}
                    />
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
                        {vehicle.location}
                      </Typography>
                    </Box>

                    {/* Features */}
                    {vehicle.features.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap" sx={{ gap: 0.5 }}>
                          {vehicle.features.slice(0, 3).map((feature: string, index: number) => (
                            <Chip key={index} label={feature} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      </Box>
                    )}
                  </Card.Body>

                  <Card.Footer>
                    <Box sx={{ display: "flex", gap: 1, width: "100%" }}>
                      <Button variant="outline" fullWidth size="sm">
                        View Details
                      </Button>
                      <Button variant="primary" fullWidth size="sm">
                        Contact Dealer
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
  );
}

export default function DashboardResultsPage() {
  return (
    <Suspense fallback={<Spinner fullScreen text="Loading results..." />}>
      <ResultsContent />
    </Suspense>
  );
}
