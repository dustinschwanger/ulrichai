import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { setUser, setLoading, logout, selectAccessToken } from '../../store/slices/authSlice';
import { useGetProfileQuery } from '../../store/api/authApi';

const AuthCheck: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();
  const accessToken = useAppSelector(selectAccessToken);

  // Query user profile if we have a token
  const { data: profile, isLoading, error } = useGetProfileQuery(undefined, {
    skip: !accessToken,
  });

  useEffect(() => {
    if (accessToken) {
      if (isLoading) {
        dispatch(setLoading(true));
      } else if (profile) {
        // Map backend profile to frontend user format
        dispatch(setUser({
          id: profile.id,
          email: profile.email,
          firstName: profile.first_name,
          lastName: profile.last_name,
          role: profile.role as any,
          organizationId: profile.organization_id,
          avatarUrl: profile.avatar_url,
          companyName: profile.company_name,
          jobTitle: profile.job_title,
          department: profile.department,
        }));
      } else if (error) {
        // Token is invalid or expired
        dispatch(logout());
      }
    } else {
      dispatch(setLoading(false));
    }
  }, [accessToken, profile, isLoading, error, dispatch]);

  return <>{children}</>;
};

export default AuthCheck;