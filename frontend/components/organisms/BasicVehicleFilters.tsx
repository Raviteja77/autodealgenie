import {
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  TextField,
} from "@mui/material";
import { DirectionsCar as DirectionsCarIcon, LocationOn as LocationOnIcon } from "@mui/icons-material";
import { Input } from "@/components";

interface BasicVehicleFiltersProps {
  make: string;
  model: string;
  carType: string;
  zipCode: string;
  searchRadius: number;
  bodyType: string;
  onMakeChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onCarTypeChange: (value: string) => void;
  onBodyTypeChange: (value: string) => void;
  onMaxResultsChange: (value: number) => void;
  onZipCodeChange: (value: string) => void;
  onSearchRadiusChange: (value: number) => void;
  makes: string[];
  models: Record<string, string[]>;
  carTypes: string[];
  bodyTypes: string[];
  maxResults: number;
}

export function BasicVehicleFilters({
  make,
  model,
  carType,
  zipCode,
  searchRadius,
  onMakeChange,
  onModelChange,
  onCarTypeChange,
  onMaxResultsChange,
  onZipCodeChange,
  onSearchRadiusChange,
  makes,
  models,
  carTypes,
  maxResults,
}: BasicVehicleFiltersProps) {
  return (
    <>
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
            value={make}
            label="Make"
            onChange={(e) => onMakeChange(e.target.value)}
            aria-label="Vehicle make selection"
          >
            <MenuItem value="">Any</MenuItem>
            {makes.map((makeOption) => (
              <MenuItem key={makeOption} value={makeOption.toLowerCase()}>
                {makeOption}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      {make && (
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="model-label">Model</InputLabel>
            <Select
              labelId="model-label"
              value={model}
              label="Model"
              onChange={(e) => onModelChange(e.target.value)}
              aria-label="Vehicle model selection"
            >
              <MenuItem value="">Any</MenuItem>
              {models[make as keyof typeof models]?.map((modelOption) => (
                <MenuItem key={modelOption} value={modelOption.toLowerCase()}>
                  {modelOption}
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
            value={carType}
            label="Car Type"
            onChange={(e) => onCarTypeChange(e.target.value)}
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

      {/* <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel id="body-type-label">Body Type</InputLabel>
          <Select
            labelId="body-type-label"
            value={bodyType}
            label="Body Type"
            onChange={(e) => onBodyTypeChange(e.target.value)}
            aria-label="Body type selection"
          >
            <MenuItem value="">Any</MenuItem>
            {bodyTypes.map((type) => (
              <MenuItem key={type} value={type.toLowerCase()}>
                {type}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid> */}

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <Input
            type="number"
            value={maxResults}
            label="Max Results"
            onChange={(e) => {
              const { value } = e.target;
              const parsed = Number.parseInt(value, 10);
              onMaxResultsChange(Number.isNaN(parsed) ? 0 : parsed);
            }}
            aria-label="Max Results to fetch from API for AI to analyze"
          />
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            <LocationOnIcon color="primary" />
            Search Location
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Find vehicles near you
          </Typography>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="ZIP Code"
              value={zipCode}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, "").slice(0, 5);
                onZipCodeChange(value);
              }}
              placeholder="Enter 5-digit ZIP code"
              required
              InputProps={{
                startAdornment: (
                  <LocationOnIcon sx={{ mr: 1, color: "text.secondary" }} />
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Search Radius</InputLabel>
              <Select
                value={searchRadius}
                onChange={(e) => onSearchRadiusChange(Number(e.target.value))}
                label="Search Radius"
                inputProps={{
                  "aria-label": "Search Radius",
                }}
              >
                <MenuItem value={25}>25 miles</MenuItem>
                <MenuItem value={50}>50 miles</MenuItem>
                <MenuItem value={100}>100 miles</MenuItem>
                <MenuItem value={200}>200 miles</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Grid>
    </>
  );
}
