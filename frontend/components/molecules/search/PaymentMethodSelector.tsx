import {
  Box,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
} from "@mui/material";
import {
  AttachMoney as AttachMoneyIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
} from "@mui/icons-material";

interface PaymentMethodSelectorProps {
  value: "cash" | "finance" | "both";
  onChange: (value: "cash" | "finance" | "both") => void;
}

export function PaymentMethodSelector({
  value,
  onChange,
}: PaymentMethodSelectorProps) {
  return (
    <>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ display: "flex", alignItems: "center", gap: 1 }}
      >
        <AccountBalanceIcon color="primary" />
        How Will You Pay?
      </Typography>
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={(_, newValue) => {
          if (newValue !== null) {
            onChange(newValue);
          }
        }}
        fullWidth
        sx={{ mt: 2 }}
      >
        <ToggleButton value="cash">
          <Box sx={{ textAlign: "center", py: 1 }}>
            <AttachMoneyIcon sx={{ fontSize: 32, mb: 1 }} />
            <Typography variant="body2">Pay Cash</Typography>
            <Typography variant="caption" color="text.secondary">
              Full payment upfront
            </Typography>
          </Box>
        </ToggleButton>
        <ToggleButton value="finance">
          <Box sx={{ textAlign: "center", py: 1 }}>
            <AccountBalanceIcon sx={{ fontSize: 32, mb: 1 }} />
            <Typography variant="body2">Finance</Typography>
            <Typography variant="caption" color="text.secondary">
              Monthly payments
            </Typography>
          </Box>
        </ToggleButton>
        <ToggleButton value="both">
          <Box sx={{ textAlign: "center", py: 1 }}>
            <TrendingUpIcon sx={{ fontSize: 32, mb: 1 }} />
            <Typography variant="body2">Show Both</Typography>
            <Typography variant="caption" color="text.secondary">
              Compare options
            </Typography>
          </Box>
        </ToggleButton>
      </ToggleButtonGroup>
    </>
  );
}
