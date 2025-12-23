import { Box, Typography, Slider } from "@mui/material";
import { AttachMoney as AttachMoneyIcon } from "@mui/icons-material";

interface BudgetRangeSliderProps {
  min: number;
  max: number;
  onChange: (min: number, max: number) => void;
  paymentMethod: "cash" | "finance" | "both";
  error?: string;
}

export function BudgetRangeSlider({
  min,
  max,
  onChange,
  paymentMethod,
  error,
}: BudgetRangeSliderProps) {
  const getTitle = () => {
    if (paymentMethod === "cash") return "Budget";
    if (paymentMethod === "finance") return "Vehicle Price Range";
    return "Price Range";
  };

  return (
    <>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ display: "flex", alignItems: "center", gap: 1 }}
      >
        <AttachMoneyIcon color="primary" />
        {getTitle()}
      </Typography>
      <Box sx={{ px: 2 }}>
        <Typography
          variant="body2"
          color="text.secondary"
          gutterBottom
          id="budget-slider-label"
        >
          ${min.toLocaleString()} - ${max.toLocaleString()}
        </Typography>
        <Slider
          value={[min, max]}
          onChange={(_, newValue) => {
            const [newMin, newMax] = newValue as number[];
            onChange(newMin, newMax);
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
          sx={{ color: "success.light" }}
          aria-labelledby="budget-slider-label"
          aria-label="Budget range slider"
        />
        {error && (
          <Typography variant="caption" color="error" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
    </>
  );
}
