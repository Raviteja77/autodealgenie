"use client";

import { Footer, Header, ProgressStepper } from "@/components";
import { Container } from "@mui/material";
import React from "react";
import { useStepper } from "@/app/context";

interface DashboardLayoutProps {
  children: React.ReactNode;
  hideStepper?: boolean; // Optional override to force hide stepper
}

function DashboardLayout({ children, hideStepper = false }: DashboardLayoutProps) {
  const { currentStep, steps, navigateToStep, shouldShowStepper } = useStepper();
  
  // Determine if stepper should be shown:
  // - Hidden if hideStepper prop is true (manual override)
  // - Otherwise, use the context's shouldShowStepper logic based on current path
  const showStepper = !hideStepper && shouldShowStepper();

  return (
    <>
      <Header />
      <Container maxWidth="xl" sx={{ pt: 12, pb: 12, flexGrow: 1 }}>
        {showStepper && (
          <ProgressStepper
            activeStep={currentStep}
            steps={steps.map(step => step.label)}
            onStepClick={navigateToStep}
          />
        )}
        {children}
      </Container>
      <Footer />
    </>
  );
}

export default DashboardLayout;