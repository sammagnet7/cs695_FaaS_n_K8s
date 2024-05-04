import PropTypes from 'prop-types';
import { useState } from 'react';

import { useNavigate } from 'react-router-dom';

// material-ui
import { useTheme, styled } from '@mui/material/styles';
import { Avatar, Box, Button, Grid, Typography } from '@mui/material';


// project imports
import MainCard from '../../../ui-component/cards/MainCard';
import SkeletonTotalOrderCard from '../../../ui-component/cards/Skeleton/EarningCard';


// assets
import LocalMallOutlinedIcon from '@mui/icons-material/LocalMallOutlined';
import StorageIcon from '@mui/icons-material/Storage';
import { ArrowUpwardTwoTone } from '@mui/icons-material';

const CardWrapper = styled(MainCard)(({ theme }) => ({
  backgroundColor: theme.palette.primary.dark,
  color: '#fff',
  overflow: 'hidden',
  position: 'relative',
  '&>div': {
    position: 'relative',
    zIndex: 5
  },
  '&:after': {
    content: '""',
    position: 'absolute',
    width: 210,
    height: 210,
    background: theme.palette.primary[800],
    borderRadius: '50%',
    zIndex: 1,
    top: -85,
    right: -95,
    [theme.breakpoints.down('sm')]: {
      top: -105,
      right: -140
    }
  },
  '&:before': {
    content: '""',
    position: 'absolute',
    zIndex: 1,
    width: 210,
    height: 210,
    background: theme.palette.primary[800],
    borderRadius: '50%',
    top: -125,
    right: -15,
    opacity: 0.5,
    [theme.breakpoints.down('sm')]: {
      top: -155,
      right: -70
    }
  }
}));

// ==============================|| DASHBOARD - TOTAL ORDER LINE CHART CARD ||============================== //

const S4Datastore = ({ isLoading }) => {
  const theme = useTheme();

  const [timeValue, setTimeValue] = useState(false);
  const handleChangeTime = (event, newValue) => {
    setTimeValue(newValue);
  };
  const navigate = useNavigate();

  const handleCardClick = () => {
    // Navigate to the /register path
    navigate("/s4");
  };
  return (
    <>
      {isLoading ? (
        <SkeletonTotalOrderCard />
      ) : (
        <CardWrapper border={false} content={false} onClick={handleCardClick}>
          <Box sx={{ p: 2.25 }}>
            <Grid container direction="column">
              <Grid item>
                <Grid container justifyContent="space-between">
                  <Grid item>
                    <Avatar
                      variant="rounded"
                      sx={{
                        ...theme.typography.commonAvatar,
                        ...theme.typography.largeAvatar,
                        backgroundColor: theme.palette.primary[800],
                        color: '#fff',
                        mt: 1
                      }}
                    >
                      <StorageIcon fontSize="inherit" />
                    </Avatar>
                  </Grid>
                </Grid>
              </Grid>
              <Grid item sx={{ mb: 0.75 }}>
                <Grid container alignItems="center">
                  <Grid item>
                    <Typography sx={{ fontSize: '1.7rem', fontWeight: 300, mr: 1, mt: 1.75, mb: 0.75 }}>S4 Service</Typography> 
                    </Grid>
                    <Grid item>
                      <Avatar
                        sx={{
                          ...theme.typography.smallAvatar,
                          cursor: 'pointer',
                          backgroundColor: theme.palette.primary[200],
                          color: theme.palette.primary.dark
                        }}
                      >
                        <ArrowUpwardTwoTone fontSize="inherit" sx={{ transform: 'rotate3d(1, 1, 1, 45deg)' }} />
                      </Avatar>
                    </Grid>
                  </Grid>
                </Grid>
                <Grid item xs={12}>
                        <Typography
                          sx={{
                            fontSize: '1rem',
                            fontWeight: 500,
                            color: theme.palette.primary[200]
                          }}
                        >
                          Datastore
                        </Typography>
                </Grid>
              </Grid>
          </Box>
        </CardWrapper>
      )}
    </>
  );
};

S4Datastore .propTypes = {
  isLoading: PropTypes.bool
};

export default S4Datastore ;
