"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import { Input, Button, Card } from "@/components";
import SearchIcon from "@mui/icons-material/Search";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import SpeedIcon from "@mui/icons-material/Speed";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Slider from "@mui/material/Slider";
import Paper from "@mui/material/Paper";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import ProgressStepper from "@/components/common/ProgressStepper";

export default function DashboardSearchPage() {
  const router = useRouter();
  const [searchParams, setSearchParams] = useState({
    make: "",
    model: "",
    yearMin: 2015,
    yearMax: 2024,
    budgetMin: 10000,
    budgetMax: 50000,
    mileageMax: 100000,
    carType: "",
    fuelType: "",
    transmission: "",
    userPriorities: "",
  });

  const handleSearch = () => {
    // Convert search params to query string
    const queryParams = new URLSearchParams();
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });
    router.push(`/dashboard/results?${queryParams.toString()}`);
  };

  const make = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz", "Volkswagen", "Audi", "Hyundai"];
  const model = ["Camry", "Accord", "F-150", "Silverado", "Altima", "3 Series", "C-Class", "Golf", "A4", "Elantra"];
  const carTypes = ["Sedan", "SUV", "Truck", "Coupe", "Hatchback", "Convertible", "Wagon", "Van"];
  const fuelTypes = ["Gasoline", "Diesel", "Electric", "Hybrid", "Plug-in Hybrid"];
  const transmissions = ["Automatic", "Manual", "CVT"];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
      <Box sx={{ pt: 10, pb: 4, bgcolor: "background.default", flexGrow: 1 }}>
        <Container maxWidth="lg">
          <ProgressStepper
            activeStep={0}
            steps={["Search", "Results", "Negotiate", "Evaluate", "Finalize"]}
          />
          {/* Header */}
          <Box sx={{ textAlign: "center", mb: 6 }}>
            <Typography variant="h3" gutterBottom fontWeight={700}>
              Find Your Perfect Car
            </Typography>
            <Typography variant="h6" color="text.secondary">
              AI-powered search to help you discover the best deals
            </Typography>
          </Box>

        {/* Search Form */}
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Grid container spacing={3}>
            {/* Basic Info */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <DirectionsCarIcon color="primary" />
                Vehicle Details
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Make</InputLabel>
                <Select
                  value={searchParams.make}
                  label="Make"
                  onChange={(e) => setSearchParams({ ...searchParams, make: e.target.value })}
                >
                  <MenuItem value="">Any</MenuItem>
                  {make.map((type) => (
                    <MenuItem key={type} value={type.toLowerCase()}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Model</InputLabel>
                <Select
                  value={searchParams.model}
                  label="Model"
                  onChange={(e) => setSearchParams({ ...searchParams, model: e.target.value })}
                >
                  <MenuItem value="">Any</MenuItem>
                  {model.map((type) => (
                    <MenuItem key={type} value={type.toLowerCase()}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Car Type</InputLabel>
                <Select
                  value={searchParams.carType}
                  label="Car Type"
                  onChange={(e) => setSearchParams({ ...searchParams, carType: e.target.value })}
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

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Fuel Type</InputLabel>
                <Select
                  value={searchParams.fuelType}
                  label="Fuel Type"
                  onChange={(e) => setSearchParams({ ...searchParams, fuelType: e.target.value })}
                >
                  <MenuItem value="">Any</MenuItem>
                  {fuelTypes.map((type) => (
                    <MenuItem key={type} value={type.toLowerCase().replace(" ", "_")}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Transmission</InputLabel>
                <Select
                  value={searchParams.transmission}
                  label="Transmission"
                  onChange={(e) => setSearchParams({ ...searchParams, transmission: e.target.value })}
                >
                  <MenuItem value="">Any</MenuItem>
                  {transmissions.map((type) => (
                    <MenuItem key={type} value={type.toLowerCase()}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Year Range */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1, mt: 2 }}>
                <CalendarTodayIcon color="primary" />
                Year Range
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ px: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {searchParams.yearMin} - {searchParams.yearMax}
                </Typography>
                <Slider
                  value={[searchParams.yearMin, searchParams.yearMax]}
                  onChange={(_, newValue) => {
                    const [min, max] = newValue as number[];
                    setSearchParams({ ...searchParams, yearMin: min, yearMax: max });
                  }}
                  valueLabelDisplay="auto"
                  min={2000}
                  max={2024}
                  marks={[
                    { value: 2000, label: "2000" },
                    { value: 2024, label: "2024" },
                  ]}
                />
              </Box>
            </Grid>

            {/* Budget */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1, mt: 2 }}>
                <AttachMoneyIcon color="primary" />
                Budget
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ px: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  ${searchParams.budgetMin.toLocaleString()} - ${searchParams.budgetMax.toLocaleString()}
                </Typography>
                <Slider
                  value={[searchParams.budgetMin, searchParams.budgetMax]}
                  onChange={(_, newValue) => {
                    const [min, max] = newValue as number[];
                    setSearchParams({ ...searchParams, budgetMin: min, budgetMax: max });
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
                />
              </Box>
            </Grid>

            {/* Mileage */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1, mt: 2 }}>
                <SpeedIcon color="primary" />
                Maximum Mileage
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ px: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Up to {searchParams.mileageMax.toLocaleString()} miles
                </Typography>
                <Slider
                  value={searchParams.mileageMax}
                  onChange={(_, newValue) =>
                    setSearchParams({ ...searchParams, mileageMax: newValue as number })
                  }
                  valueLabelDisplay="auto"
                  min={10000}
                  max={200000}
                  step={10000}
                  valueLabelFormat={(value) => `${value.toLocaleString()} mi`}
                  marks={[
                    { value: 10000, label: "10K" },
                    { value: 200000, label: "200K" },
                  ]}
                />
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ px: 2 }}>
                <Input multiLine={true} fullWidth label="Your Priorities (Optional)"  />
              </Box>
            </Grid>

            {/* Search Button */}
            <Grid item xs={12}>
              <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end", mt: 3 }}>
                <Button
                  variant="outline"
                  onClick={() =>
                    setSearchParams({
                      make: "",
                      model: "",
                      yearMin: 2015,
                      yearMax: 2024,
                      budgetMin: 10000,
                      budgetMax: 50000,
                      mileageMax: 100000,
                      carType: "",
                      fuelType: "",
                      transmission: "",
                      userPriorities: "",
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

        {/* Quick Search Presets */}
        <Box sx={{ mt: 6 }}>
          <Typography variant="h5" gutterBottom fontWeight={600}>
            Popular Searches
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {[
              { title: "Family SUVs", make: "Toyota", carType: "suv", budgetMax: 40000 },
              { title: "Luxury Sedans", carType: "sedan", budgetMin: 30000 },
              { title: "Fuel Efficient", fuelType: "hybrid", mileageMax: 50000 },
              { title: "Budget Friendly", budgetMax: 15000 },
            ].map((preset, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card hover shadow="sm" sx={{ cursor: "pointer" }} onClick={() => setSearchParams({ ...searchParams, ...preset })}>
                  <Card.Body>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      {preset.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Click to apply filter
                    </Typography>
                  </Card.Body>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
        </Container>
      </Box>
      <Footer />
    </Box>
  );
}
