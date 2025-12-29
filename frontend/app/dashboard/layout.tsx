"use client";

import { Footer, Header, ProgressStepper } from "@/components";
import { Container } from "@mui/material";
import React from "react";
import { useStepper } from "@/app/context";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

function DashboardLayout({ children }: DashboardLayoutProps) {
  const { currentStep, steps, navigateToStep, shouldShowStepper } = useStepper();
  
  const showStepper = shouldShowStepper();

  return (
    <>
      <Header />
      <Container maxWidth="xl" sx={{ pt: 16, pb: 6, flexGrow: 1 }}>
        {showStepper && (
          <Container maxWidth="xl">
            <ProgressStepper
              activeStep={currentStep}
              steps={steps.map(step => step.label)}
              onStepClick={navigateToStep}
            />
          </Container>
        )}
        {children}
      </Container>
      <Footer />
    </>
  );
}

export default DashboardLayout;