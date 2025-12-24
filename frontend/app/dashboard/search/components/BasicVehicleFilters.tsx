import {
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
} from "@mui/material";
import { DirectionsCar as DirectionsCarIcon } from "@mui/icons-material";
import { Input } from "@/components";

interface BasicVehicleFiltersProps {
  make: string;
  model: string;
  carType: string;
  bodyType: string;
  onMakeChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onCarTypeChange: (value: string) => void;
  onBodyTypeChange: (value: string) => void;
  onMaxResultsChange: (value: number) => void;
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
  bodyType,
  onMakeChange,
  onModelChange,
  onCarTypeChange,
  onBodyTypeChange,
  onMaxResultsChange,
  makes,
  models,
  carTypes,
  bodyTypes,
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
    </>
  );
}
