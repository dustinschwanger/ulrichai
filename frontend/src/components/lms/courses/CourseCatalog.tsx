import React, { useState, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Chip,
  Rating,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Pagination,
  Skeleton,
  IconButton,
  Paper,
  Drawer,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  Avatar,
  AvatarGroup,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Search,
  FilterList,
  School,
  AccessTime,
  People,
  TrendingUp,
  LocalOffer,
  Clear,
  ExpandMore,
  ExpandLess,
  Star,
  BookmarkBorder,
  Bookmark,
  PlayCircleOutline,
  Article,
  Quiz,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useGetCoursesQuery } from '../../../features/lms/courseBuilderSlice';

interface FilterState {
  category: string;
  difficulty: string[];
  duration: [number, number];
  rating: number;
  price: string;
  features: string[];
}

const CourseCatalog: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('popular');
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(true);
  const [bookmarkedCourses, setBookmarkedCourses] = useState<string[]>([]);

  const [filters, setFilters] = useState<FilterState>({
    category: 'all',
    difficulty: [],
    duration: [0, 100],
    rating: 0,
    price: 'all',
    features: [],
  });

  // Fetch courses from API - only show published courses
  const { data: allCourses, isLoading } = useGetCoursesQuery();

  // Filter for published courses only
  const publishedCourses = useMemo(() => {
    return allCourses?.filter((course: any) => course.is_published) || [];
  }, [allCourses]);

  // Categories for filter
  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'technology', label: 'Technology' },
    { value: 'business', label: 'Business' },
    { value: 'design', label: 'Design' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'personal', label: 'Personal Development' },
    { value: 'health', label: 'Health & Fitness' },
  ];

  // Apply filters and sorting (but not pagination) to published courses
  const filteredCoursesBeforePagination = useMemo(() => {
    let filtered = [...publishedCourses];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(course => course.category === filters.category);
    }

    // Apply difficulty filter
    if (filters.difficulty.length > 0) {
      filtered = filtered.filter(course =>
        filters.difficulty.includes(course.difficulty_level || 'beginner')
      );
    }

    // Apply sorting
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case 'popular':
      default:
        // For now, sort by is_featured then by created_at
        filtered.sort((a, b) => {
          if (a.is_featured && !b.is_featured) return -1;
          if (!a.is_featured && b.is_featured) return 1;
          return 0;
        });
        break;
    }

    return filtered;
  }, [publishedCourses, searchTerm, filters, sortBy]);

  // Apply pagination to filtered courses
  const filteredCourses = useMemo(() => {
    const start = (page - 1) * 12;
    const end = start + 12;
    return filteredCoursesBeforePagination.slice(start, end);
  }, [filteredCoursesBeforePagination, page]);

  const handleToggleBookmark = (courseId: string) => {
    setBookmarkedCourses(prev =>
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    );
  };

  const handleFilterChange = (filterType: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value,
    }));
    setPage(1); // Reset to first page when filters change
  };

  const handleClearFilters = () => {
    setFilters({
      category: 'all',
      difficulty: [],
      duration: [0, 100],
      rating: 0,
      price: 'all',
      features: [],
    });
    setSearchTerm('');
  };

  const handleEnroll = (courseId: string) => {
    // TODO: Implement enrollment logic
    navigate(`/lms/course/${courseId}`);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Course Catalog
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Explore our collection of courses designed to help you achieve your goals
        </Typography>
      </Box>

      {/* Search and Sort Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setSearchTerm('')}>
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="popular">Most Popular</MenuItem>
                <MenuItem value="newest">Newest First</MenuItem>
                <MenuItem value="rating">Highest Rated</MenuItem>
                <MenuItem value="price-low">Price: Low to High</MenuItem>
                <MenuItem value="price-high">Price: High to Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              endIcon={showFilters ? <ExpandLess /> : <ExpandMore />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Filters Drawer */}
      <Drawer
        anchor="left"
        open={showFilters}
        onClose={() => setShowFilters(false)}
        PaperProps={{
          sx: { width: 320, p: 3 }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Filters</Typography>
          <Button size="small" onClick={handleClearFilters}>
            Clear All
          </Button>
        </Box>

              {/* Category Filter */}
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category}
                  label="Category"
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                >
                  {categories.map(cat => (
                    <MenuItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Difficulty Filter */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Difficulty Level
                </Typography>
                <FormGroup>
                  {['beginner', 'intermediate', 'advanced'].map(level => (
                    <FormControlLabel
                      key={level}
                      control={
                        <Checkbox
                          checked={filters.difficulty.includes(level)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              handleFilterChange('difficulty', [...filters.difficulty, level]);
                            } else {
                              handleFilterChange('difficulty',
                                filters.difficulty.filter(d => d !== level)
                              );
                            }
                          }}
                        />
                      }
                      label={level.charAt(0).toUpperCase() + level.slice(1)}
                    />
                  ))}
                </FormGroup>
              </Box>

              {/* Duration Filter */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Duration (hours)
                </Typography>
                <Slider
                  value={filters.duration}
                  onChange={(e, value) => handleFilterChange('duration', value)}
                  valueLabelDisplay="auto"
                  min={0}
                  max={100}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100+' },
                  ]}
                />
              </Box>

              {/* Rating Filter */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Minimum Rating
                </Typography>
                <Rating
                  value={filters.rating}
                  onChange={(e, value) => handleFilterChange('rating', value || 0)}
                  precision={0.5}
                />
              </Box>

              {/* Features Filter */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Features
                </Typography>
                <FormGroup>
                  {[
                    { value: 'certificate', label: 'Certificate' },
                    { value: 'ai-powered', label: 'AI-Powered' },
                    { value: 'projects', label: 'Projects' },
                    { value: 'subtitles', label: 'Subtitles' },
                  ].map(feature => (
                    <FormControlLabel
                      key={feature.value}
                      control={
                        <Checkbox
                          checked={filters.features.includes(feature.value)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              handleFilterChange('features', [...filters.features, feature.value]);
                            } else {
                              handleFilterChange('features',
                                filters.features.filter(f => f !== feature.value)
                              );
                            }
                          }}
                        />
                      }
                      label={feature.label}
                    />
                  ))}
                </FormGroup>
              </Box>
      </Drawer>

      {/* Course Grid */}
      <Box>
          {/* Results Summary */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {isLoading ? 'Loading...' : `${filteredCoursesBeforePagination.length} courses found`}
            </Typography>
            {filteredCourses.length > 0 && (
              <Pagination
                count={Math.ceil((filteredCoursesBeforePagination.length || 0) / 12)}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
                size="small"
              />
            )}
          </Box>

          <Grid container spacing={3}>
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 6 }).map((_, index) => (
                <Grid item xs={12} sm={6} lg={4} key={index}>
                  <Card>
                    <Skeleton variant="rectangular" height={180} />
                    <CardContent>
                      <Skeleton variant="text" height={32} />
                      <Skeleton variant="text" width="80%" />
                      <Skeleton variant="text" width="60%" />
                    </CardContent>
                  </Card>
                </Grid>
              ))
            ) : filteredCourses.length === 0 ? (
              <Grid item xs={12}>
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                  <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No courses found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Try adjusting your filters or search term
                  </Typography>
                </Paper>
              </Grid>
            ) : (
              // Course cards
              filteredCourses.map((course) => (
                <Grid item xs={12} sm={6} lg={4} key={course.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      position: 'relative',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 3,
                      },
                    }}
                  >
                    {/* Featured Badge */}
                    {course.is_featured && (
                      <Badge
                        sx={{
                          position: 'absolute',
                          top: 10,
                          left: 10,
                          zIndex: 1,
                        }}
                      >
                        <Chip
                          label="Featured"
                          color="primary"
                          size="small"
                          icon={<Star />}
                        />
                      </Badge>
                    )}

                    {/* Bookmark Button */}
                    <IconButton
                      sx={{
                        position: 'absolute',
                        top: 10,
                        right: 10,
                        zIndex: 1,
                        bgcolor: 'background.paper',
                        '&:hover': { bgcolor: 'background.paper' },
                      }}
                      onClick={() => handleToggleBookmark(course.id)}
                    >
                      {bookmarkedCourses.includes(course.id) ? (
                        <Bookmark color="primary" />
                      ) : (
                        <BookmarkBorder />
                      )}
                    </IconButton>

                    {/* Course Image */}
                    <CardMedia
                      component="img"
                      height="180"
                      image={course.thumbnail}
                      alt={course.title}
                      sx={{ objectFit: 'cover', cursor: 'pointer' }}
                      onClick={() => navigate(`/lms/course/${course.id}`)}
                    />

                    <CardContent sx={{ flex: 1 }}>
                      {/* Category & Level */}
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip
                          label={course.category || 'General'}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={course.level}
                          size="small"
                          color={
                            course.level === 'beginner'
                              ? 'success'
                              : course.level === 'intermediate'
                              ? 'warning'
                              : 'error'
                          }
                        />
                      </Box>

                      {/* Title */}
                      <Typography variant="h6" gutterBottom sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        minHeight: '3em',
                      }}>
                        {course.title}
                      </Typography>

                      {/* Instructor */}
                      {course.instructor && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
                          <Avatar
                            sx={{ width: 24, height: 24 }}
                          >
                            {course.instructor.first_name?.[0]}{course.instructor.last_name?.[0]}
                          </Avatar>
                          <Typography variant="body2" color="text.secondary">
                            {course.instructor.first_name} {course.instructor.last_name}
                          </Typography>
                        </Box>
                      )}

                      {/* Course Info */}
                      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTime sx={{ fontSize: 16, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {course.duration_hours || 0}h
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <PlayCircleOutline sx={{ fontSize: 16, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {course.lesson_count || 0} activities
                          </Typography>
                        </Box>
                        {course.module_count > 0 && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <School sx={{ fontSize: 16, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary">
                              {course.module_count} modules
                            </Typography>
                          </Box>
                        )}
                      </Box>

                      {/* Tags */}
                      {course.tags && course.tags.length > 0 && (
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
                          {course.tags.slice(0, 3).map((tag: string) => (
                            <Chip
                              key={tag}
                              label={tag}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      )}

                      {/* Difficulty Level */}
                      {course.difficulty_level && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Level:
                          </Typography>
                          <Chip
                            label={course.difficulty_level}
                            size="small"
                            color={course.difficulty_level === 'beginner' ? 'success' : course.difficulty_level === 'intermediate' ? 'warning' : 'error'}
                          />
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ p: 2, pt: 0 }}>
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => handleEnroll(course.id)}
                        sx={{
                          background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                          '&:hover': {
                            background: 'linear-gradient(45deg, #5a67d8 30%, #6b4199 90%)',
                          },
                        }}
                      >
                        Enroll Now
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>

          {/* Bottom Pagination */}
          {filteredCourses.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={Math.ceil((filteredCoursesBeforePagination.length || 0) / 12)}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
      </Box>
    </Box>
  );
};

export default CourseCatalog;