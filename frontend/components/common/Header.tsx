"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import {
  AppBar,
  Box,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  Avatar,
  Button,
  Tooltip,
  MenuItem,
  Skeleton,
} from "@mui/material";
// import { signOut } from "firebase/auth";
// import { auth } from "@/app/firebase";
// import { useRouter } from "next/navigation";
import Link from "next/link";
// import { useAuth } from "@/app/context/AuthProvider";

function Header() {
  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
//   const { user, loading } = useAuth();
//   const router = useRouter();

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

//   const handleSignOut = async () => {
//     handleCloseUserMenu();
//     await signOut(auth);
//     router.push("/auth/login");
//   };
  return (
    <AppBar
      position="fixed"
      color="primary"
      elevation={0}
      sx={{ bgcolor: "white", borderBottom: "1px solid #e0e0e0" }}
    >
      <Toolbar>
        <Image
          src="/logo.png"
          alt="Auto deal genie logomark"
          width={40}
          height={40}
        />
        <Typography
          variant="h6"
          noWrap
          component={Link}
          href="/"
          sx={{ flexGrow: 1, color: "text.primary", fontWeight: 700 }}
        >
          Auto Deal Genie
        </Typography>
        <Box sx={{ flexGrow: 1 }} />

        {/* <Box sx={{ flexGrow: 0 }}>
          {loading ? (
            <Skeleton variant="circular" width={40} height={40} />
          ) : user ? (
            <>
              <Tooltip title="Open settings">
                <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                  <Avatar
                    alt={user.displayName || "User"}
                    src={user.photoURL || ""}
                  />
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
                    {user.displayName || user.email}
                  </Typography>
                </MenuItem>
                <MenuItem onClick={handleSignOut}>
                  <Typography textAlign="center">Sign Out</Typography>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button color="inherit" component={Link} href="/auth/login">
              Login
            </Button>
          )}
        </Box> */}
      </Toolbar>
    </AppBar>
  );
}

export default Header;
