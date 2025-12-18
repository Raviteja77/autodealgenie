"use client";

import Image from "next/image";
import {
  AppBar,
  Avatar,
  Box,
  Container,
  IconButton,
  Menu,
  MenuItem,
  Skeleton,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useState } from "react";
import { Button } from "../ui/Button";

function Header() {
  const { user, loading, logout } = useAuth();
  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
  const router = useRouter();

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleSignOut = async () => {
    handleCloseUserMenu();
    await logout();
    router.push("/auth/login");
  };

  const stringToColor = (string: string) => {
    let hash = 0;
    // Curated palette of rich, luxury-style colors (Deep Jewel Tones)
    const colors = [
      "#0D47A1", // Deep Blue
      "#1B5E20", // Deep Green
      "#B71C1C", // Deep Red
      "#4A148C", // Deep Purple
      "#3E2723", // Deep Brown
      "#263238", // Deep Blue Grey
      "#880E4F", // Deep Burgundy
      "#006064", // Deep Cyan
      "#BF360C", // Deep Orange
      "#311B92", // Deep Indigo
    ];

    /* eslint-disable no-bitwise */
    for (let i = 0; i < string.length; i += 1) {
      hash = string.charCodeAt(i) + ((hash << 5) - hash);
    }

    const index = Math.abs(hash) % colors.length;
    return colors[index];
  };

  return (
    <AppBar
      position="fixed"
      color="primary"
      elevation={0}
      sx={{ bgcolor: "white", borderBottom: "1px solid #e0e0e0" }}
    >
      <Toolbar>
        <Container maxWidth="lg" sx={{ display: "flex", alignItems: "center" }}>
          <Link href="/" style={{ display: "flex", alignItems: "center" }}>
            <Image
              src="/images/icon.png"
              alt="Auto deal genie logomark"
              width={64}
              height={64}
            />
            <Typography
              variant="h5"
              noWrap
              sx={{ color: "text.primary", fontWeight: 700 }}
            >
              Auto Deal Genie
            </Typography>
          </Link>
          <Box sx={{ flexGrow: 1 }} />

          <Box sx={{ flexGrow: 0 }}>
            {loading ? (
              <Skeleton variant="circular" width={40} height={40} />
            ) : user ? (
              <>
                <Tooltip title="Open settings">
                  <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                    <Avatar
                      alt={user.username || "User"}
                      sx={{
                        background: `linear-gradient(45deg, ${stringToColor(
                          user.username || user.email || "U"
                        )} 30%, #000000 90%)`,
                      }}
                    >
                      {(user.username || user.email || "U")
                        .charAt(0)
                        .toUpperCase()}
                    </Avatar>
                  </IconButton>
                </Tooltip>
                <Menu
                  sx={{ mt: "45px" }}
                  id="menu-appbar"
                  anchorEl={anchorElUser}
                  anchorOrigin={{
                    vertical: "top",
                    horizontal: "right",
                  }}
                  keepMounted
                  transformOrigin={{
                    vertical: "top",
                    horizontal: "right",
                  }}
                  open={Boolean(anchorElUser)}
                  onClose={handleCloseUserMenu}
                >
                  <MenuItem disabled>
                    <Typography textAlign="center">
                      {user.full_name || user.email}
                    </Typography>
                  </MenuItem>
                  <MenuItem onClick={handleSignOut}>
                    <Typography textAlign="center">Sign Out</Typography>
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <Button variant="outline" component={Link} href="/auth/login">
                Login
              </Button>
            )}
          </Box>
        </Container>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
