"use client";

import {
  Stepper,
  Step,
  StepLabel,
  Box,
  StepConnector,
  styled,
  stepConnectorClasses,
} from "@mui/material";
import { StepIconProps } from "@mui/material/StepIcon";
import CheckIcon from "@mui/icons-material/Check";

interface ProgressStepperProps {
  activeStep: number;
  steps: string[];
  onStepClick?: (step: number) => void;
}

// Shared gradient constant
const SUCCESS_GRADIENT =
  "linear-gradient(95deg, rgb(22,163,74) 0%, rgb(34,197,94) 50%, rgb(74,222,128) 100%)";
const SUCCESS_GRADIENT_ICON =
  "linear-gradient(136deg, rgb(22,163,74) 0%, rgb(34,197,94) 50%, rgb(74,222,128) 100%)";

// Custom Stepper Styling
const ColorlibConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      backgroundImage: SUCCESS_GRADIENT,
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      "& .MuiStepConnector-line": {
        backgroundImage: SUCCESS_GRADIENT,
      },
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    height: 3,
    border: 0,
    backgroundColor:
      theme.palette.mode === "dark" ? theme.palette.grey[800] : "#eaeaf0",
    borderRadius: 1,
  },
}));

const ColorlibStepIconRoot = styled("div")<{
  ownerState: { completed?: boolean; active?: boolean };
}>(({ theme, ownerState }) => ({
  backgroundColor:
    theme.palette.mode === "dark" ? theme.palette.grey[700] : "#e0e0e0",
  zIndex: 1,
  color: "#fff",
  width: 50,
  height: 50,
  display: "flex",
  borderRadius: "50%",
  justifyContent: "center",
  alignItems: "center",
  fontSize: "1.25rem",
  fontWeight: 600,
  ...(ownerState.active && {
    backgroundImage: SUCCESS_GRADIENT_ICON,
    boxShadow: "0 4px 10px 0 rgba(0,0,0,.25)",
  }),
  ...(ownerState.completed && {
    backgroundImage: SUCCESS_GRADIENT_ICON,
  }),
}));

function ColorlibStepIcon(props: StepIconProps) {
  const { active, completed, className, icon } = props;

  return (
    <ColorlibStepIconRoot
      ownerState={{ completed, active }}
      className={className}
    >
      {completed ? <CheckIcon /> : icon}
    </ColorlibStepIconRoot>
  );
}

export default function ProgressStepper({
  activeStep,
  steps,
  onStepClick,
}: ProgressStepperProps) {
  return (
    <Box sx={{ width: "100%", mb: 4 }}>
      <Stepper
        alternativeLabel
        activeStep={activeStep}
        connector={<ColorlibConnector />}
      >
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel
              role="button"
              StepIconComponent={ColorlibStepIcon}
              onClick={() => onStepClick?.(index)}
              onKeyDown={() => onStepClick?.(index)}
              sx={{ cursor: onStepClick ? "pointer" : "default" }}
            >
              {label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
}
