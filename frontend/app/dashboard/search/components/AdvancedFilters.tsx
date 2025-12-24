import {
  Box,
  Grid,
  Paper,
  Slider,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
} from "@mui/material";
import {
  CalendarToday as CalendarTodayIcon,
  Speed as SpeedIcon,
} from "@mui/icons-material";
import { Input } from "@/components";

interface AdvancedFiltersProps {
  yearMin: number;
  yearMax: number;
  mileageMax: number;
  fuelType: string;
  transmission: string;
  drivetrain: string;
  mustHaveFeatures: string[];
  userPriorities: string;
  showYearFilter: boolean;
  showMileageFilter: boolean;
  onYearChange: (min: number, max: number) => void;
  onMileageChange: (value: number) => void;
  onFuelTypeChange: (value: string) => void;
  onTransmissionChange: (value: string) => void;
  onDrivetrainChange: (value: string) => void;
  onMustHaveFeaturesChange: (value: string[]) => void;
  onUserPrioritiesChange: (value: string) => void;
  yearError?: string;
  fuelTypes: string[];
  transmissions: string[];
  drivetrains: string[];
  featureOptions: string[];
}

export function AdvancedFilters({
  yearMin,
  yearMax,
  mileageMax,
  fuelType,
  transmission,
  drivetrain,
  mustHaveFeatures,
  userPriorities,
  showYearFilter,
  showMileageFilter,
  onYearChange,
  onMileageChange,
  onFuelTypeChange,
  onTransmissionChange,
  onDrivetrainChange,
  onMustHaveFeaturesChange,
  onUserPrioritiesChange,
  yearError,
  fuelTypes,
  transmissions,
  drivetrains,
  featureOptions,
}: AdvancedFiltersProps) {
  return (
    <Paper
      id="advanced-filters-section"
      variant="outlined"
      sx={{ p: 3, bgcolor: "grey.50", borderRadius: 2 }}
      role="region"
      aria-label="Advanced search filters"
    >
      <Grid container spacing={3}>
        {/* Year Range - Conditional */}
        {showYearFilter && (
          <>
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
                  {yearMin} - {yearMax}
                </Typography>
                <Slider
                  value={[yearMin, yearMax]}
                  onChange={(_, newValue) => {
                    const [min, max] = newValue as number[];
                    onYearChange(min, max);
                  }}
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
                {yearError && (
                  <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                    {yearError}
                  </Typography>
                )}
              </Box>
            </Grid>
          </>
        )}

        {/* Mileage - Conditional */}
        {showMileageFilter && (
          <>
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
                  Up to {mileageMax.toLocaleString()} miles
                </Typography>
                <Slider
                  value={mileageMax}
                  onChange={(_, newValue) => onMileageChange(newValue as number)}
                  valueLabelDisplay="auto"
                  min={5000}
                  max={200000}
                  step={5000}
                  valueLabelFormat={(value) => `${value.toLocaleString()} mi`}
                  marks={[
                    { value: 5000, label: "5K" },
                    { value: 200000, label: "200K" },
                  ]}
                  sx={{ color: "success.light" }}
                  aria-labelledby="mileage-slider-label"
                  aria-label="Maximum mileage slider"
                />
              </Box>
            </Grid>
          </>
        )}

        {/* Fuel Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="fuel-type-label">Fuel Type</InputLabel>
            <Select
              labelId="fuel-type-label"
              value={fuelType}
              label="Fuel Type"
              onChange={(e) => onFuelTypeChange(e.target.value)}
              aria-label="Fuel type selection"
            >
              <MenuItem value="">Any</MenuItem>
              {fuelTypes.map((type) => (
                <MenuItem key={type} value={type.toLowerCase()}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Transmission */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="transmission-label">Transmission</InputLabel>
            <Select
              labelId="transmission-label"
              value={transmission}
              label="Transmission"
              onChange={(e) => onTransmissionChange(e.target.value)}
              aria-label="Transmission selection"
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

        {/* Drivetrain */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="drivetrain-label">Drivetrain</InputLabel>
            <Select
              labelId="drivetrain-label"
              value={drivetrain}
              label="Drivetrain"
              onChange={(e) => onDrivetrainChange(e.target.value)}
              aria-label="Drivetrain selection"
            >
              <MenuItem value="">Any</MenuItem>
              {drivetrains.map((type) => (
                <MenuItem key={type} value={type.toLowerCase()}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Must-Have Features */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="features-label">Must-Have Features</InputLabel>
            <Select
              labelId="features-label"
              multiple
              value={mustHaveFeatures}
              onChange={(e) =>
                onMustHaveFeaturesChange(
                  typeof e.target.value === "string"
                    ? e.target.value.split(",")
                    : e.target.value
                )
              }
              input={<OutlinedInput label="Must-Have Features" />}
              renderValue={(selected) => (
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
              aria-label="Must-have features selection"
            >
              {featureOptions.map((feature) => (
                <MenuItem key={feature} value={feature.toLowerCase()}>
                  {feature}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Additional Preferences */}
        <Grid item xs={12}>
          <Box sx={{ px: 2 }}>
            <Input
              multiLine={true}
              fullWidth
              label="Your Priorities (Optional)"
              onChange={(e) => onUserPrioritiesChange(e.target.value)}
              placeholder="e.g., fuel efficiency, safety features, low maintenance costs"
              value={userPriorities}
              aria-label="User priorities and preferences"
            />
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}
