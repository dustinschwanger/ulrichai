import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Card,
  CardContent,
  IconButton,
  Avatar,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Collapse,
  Badge,
  Grid,
} from '@mui/material';
import {
  Forum,
  Send,
  ThumbUp,
  Reply,
  MoreVert,
  Edit,
  Delete,
  PushPin,
  CheckCircle,
  ExpandMore,
  ExpandLess,
  Add,
} from '@mui/icons-material';
import {
  useGetThreadsByLessonQuery,
  useCreateThreadMutation,
  useUpdateThreadMutation,
  useDeleteThreadMutation,
  useUpvoteThreadMutation,
  useGetRepliesByThreadQuery,
  useCreateReplyMutation,
  useUpdateReplyMutation,
  useDeleteReplyMutation,
  useUpvoteReplyMutation,
  useMarkReplyAsSolutionMutation,
} from '../../../features/lms/discussionsSlice';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store/store';
import { formatDistanceToNow } from 'date-fns';
import HtmlContent from '../../common/HtmlContent';

interface DiscussionProps {
  lessonId: string;
  lessonData: any;
}

interface ThreadItemProps {
  thread: any;
  onSelect: (thread: any) => void;
  isSelected: boolean;
  currentUserId: string;
}

const ThreadItem: React.FC<ThreadItemProps> = ({ thread, onSelect, isSelected, currentUserId }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [updateThread] = useUpdateThreadMutation();
  const [deleteThread] = useDeleteThreadMutation();
  const [upvoteThread] = useUpvoteThreadMutation();
  const [editMode, setEditMode] = useState(false);
  const [editedTitle, setEditedTitle] = useState(thread.title);
  const [editedContent, setEditedContent] = useState(thread.content);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleUpvote = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await upvoteThread(thread.id);
  };

  const handleEdit = () => {
    setEditMode(true);
    handleMenuClose();
  };

  const handleSaveEdit = async () => {
    await updateThread({
      id: thread.id,
      data: {
        title: editedTitle,
        content: editedContent,
      },
    });
    setEditMode(false);
  };

  const handleDelete = async () => {
    await deleteThread(thread.id);
    handleMenuClose();
  };

  if (editMode) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack spacing={2}>
            <TextField
              fullWidth
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              label="Title"
            />
            <TextField
              fullWidth
              multiline
              rows={3}
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              label="Content"
            />
            <Stack direction="row" spacing={1}>
              <Button variant="contained" size="small" onClick={handleSaveEdit}>
                Save
              </Button>
              <Button size="small" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        mb: 2,
        cursor: 'pointer',
        bgcolor: isSelected ? 'action.selected' : 'background.paper',
        '&:hover': {
          bgcolor: 'action.hover',
        },
      }}
      onClick={() => onSelect(thread)}
    >
      <CardContent>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box flex={1}>
              <Stack direction="row" spacing={1} alignItems="center">
                {thread.is_pinned && <PushPin fontSize="small" color="primary" />}
                <Typography variant="h6">
                  {thread.title}
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {thread.content.substring(0, 150)}
                {thread.content.length > 150 && '...'}
              </Typography>
            </Box>
            {thread.author_id === currentUserId && (
              <IconButton size="small" onClick={handleMenuOpen}>
                <MoreVert fontSize="small" />
              </IconButton>
            )}
          </Stack>

          <Stack direction="row" spacing={2} alignItems="center">
            <Stack direction="row" spacing={1} alignItems="center">
              <Avatar sx={{ width: 24, height: 24 }}>
                {thread.author_name?.charAt(0) || 'U'}
              </Avatar>
              <Typography variant="caption">
                {thread.author_name || 'Unknown'}
              </Typography>
            </Stack>
            <Typography variant="caption" color="text.secondary">
              {formatDistanceToNow(new Date(thread.created_at), { addSuffix: true })}
            </Typography>
            <Chip
              icon={<Reply />}
              label={thread.replies_count || 0}
              size="small"
              variant="outlined"
            />
            <IconButton size="small" onClick={handleUpvote}>
              <Badge badgeContent={thread.upvotes} color="primary">
                <ThumbUp fontSize="small" />
              </Badge>
            </IconButton>
          </Stack>
        </Stack>

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
          <MenuItem onClick={handleEdit}>
            <Edit fontSize="small" sx={{ mr: 1 }} /> Edit
          </MenuItem>
          <MenuItem onClick={handleDelete}>
            <Delete fontSize="small" sx={{ mr: 1 }} /> Delete
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
};

interface ReplyItemProps {
  reply: any;
  currentUserId: string;
  isInstructor: boolean;
}

const ReplyItem: React.FC<ReplyItemProps> = ({ reply, currentUserId, isInstructor }) => {
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState(reply.content);
  const [updateReply] = useUpdateReplyMutation();
  const [deleteReply] = useDeleteReplyMutation();
  const [upvoteReply] = useUpvoteReplyMutation();
  const [markAsSolution] = useMarkReplyAsSolutionMutation();

  const handleSaveEdit = async () => {
    await updateReply({
      id: reply.id,
      data: { content: editedContent },
    });
    setEditMode(false);
  };

  const handleDelete = async () => {
    await deleteReply(reply.id);
  };

  const handleUpvote = async () => {
    await upvoteReply(reply.id);
  };

  const handleMarkAsSolution = async () => {
    await markAsSolution(reply.id);
  };

  return (
    <Box sx={{ pl: 4, mb: 2 }}>
      <Paper
        sx={{
          p: 2,
          bgcolor: reply.is_solution ? 'success.light' : 'background.paper',
          border: reply.is_solution ? '2px solid' : 'none',
          borderColor: 'success.main',
        }}
      >
        {editMode ? (
          <Stack spacing={2}>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
            />
            <Stack direction="row" spacing={1}>
              <Button variant="contained" size="small" onClick={handleSaveEdit}>
                Save
              </Button>
              <Button size="small" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </Stack>
          </Stack>
        ) : (
          <Stack spacing={1}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Avatar sx={{ width: 28, height: 28 }}>
                {reply.author_name?.charAt(0) || 'U'}
              </Avatar>
              <Typography variant="subtitle2">
                {reply.author_name || 'Unknown'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
              </Typography>
              {reply.is_solution && (
                <Chip
                  icon={<CheckCircle />}
                  label="Solution"
                  size="small"
                  color="success"
                />
              )}
            </Stack>

            <Typography variant="body1" sx={{ pl: 4 }}>
              {reply.content}
            </Typography>

            <Stack direction="row" spacing={1} sx={{ pl: 4 }}>
              <IconButton size="small" onClick={handleUpvote}>
                <Badge badgeContent={reply.upvotes} color="primary">
                  <ThumbUp fontSize="small" />
                </Badge>
              </IconButton>
              {reply.author_id === currentUserId && (
                <>
                  <IconButton size="small" onClick={() => setEditMode(true)}>
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={handleDelete}>
                    <Delete fontSize="small" />
                  </IconButton>
                </>
              )}
              {isInstructor && !reply.is_solution && (
                <Button
                  size="small"
                  startIcon={<CheckCircle />}
                  onClick={handleMarkAsSolution}
                >
                  Mark as Solution
                </Button>
              )}
            </Stack>
          </Stack>
        )}
      </Paper>
    </Box>
  );
};

const Discussion: React.FC<DiscussionProps> = ({ lessonId, lessonData }) => {
  const user = useSelector((state: RootState) => state.auth.user);
  const [selectedThread, setSelectedThread] = useState<any>(null);
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadContent, setNewThreadContent] = useState('');
  const [newReplyContent, setNewReplyContent] = useState('');
  const [showNewThread, setShowNewThread] = useState(false);
  const [showReplies, setShowReplies] = useState(true);

  const { data: threads, isLoading: threadsLoading } = useGetThreadsByLessonQuery(lessonId);
  const { data: replies, isLoading: repliesLoading } = useGetRepliesByThreadQuery(
    selectedThread?.id || '',
    { skip: !selectedThread }
  );

  const [createThread] = useCreateThreadMutation();
  const [createReply] = useCreateReplyMutation();

  const isInstructor = user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN';
  const requiresInitialPost = lessonData?.content_data?.require_initial_post;
  const hasPosted = threads?.some(t => t.author_id === user?.id);

  const handleCreateThread = async () => {
    if (newThreadTitle.trim() && newThreadContent.trim()) {
      await createThread({
        lesson_id: lessonId,
        title: newThreadTitle,
        content: newThreadContent,
      });
      setNewThreadTitle('');
      setNewThreadContent('');
      setShowNewThread(false);
    }
  };

  const handleCreateReply = async () => {
    if (newReplyContent.trim() && selectedThread) {
      await createReply({
        thread_id: selectedThread.id,
        content: newReplyContent,
      });
      setNewReplyContent('');
    }
  };

  const pinnedThreads = threads?.filter(t => t.is_pinned) || [];
  const regularThreads = threads?.filter(t => !t.is_pinned) || [];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <Forum sx={{ mr: 2, verticalAlign: 'middle' }} />
        Discussion: {lessonData?.title}
      </Typography>

      {lessonData?.description && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Discussion Prompt
          </Typography>
          <HtmlContent content={lessonData.description} />
        </Alert>
      )}

      {requiresInitialPost && !hasPosted && !isInstructor && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          You must create your own post before viewing others' discussions.
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Discussion Threads</Typography>
              <Button
                startIcon={<Add />}
                variant="contained"
                size="small"
                onClick={() => setShowNewThread(true)}
              >
                New Thread
              </Button>
            </Stack>

            {showNewThread && (
              <Card sx={{ mb: 2, bgcolor: 'action.hover' }}>
                <CardContent>
                  <Stack spacing={2}>
                    <TextField
                      fullWidth
                      label="Thread Title"
                      value={newThreadTitle}
                      onChange={(e) => setNewThreadTitle(e.target.value)}
                      placeholder="Enter a descriptive title..."
                    />
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Your Post"
                      value={newThreadContent}
                      onChange={(e) => setNewThreadContent(e.target.value)}
                      placeholder="Share your thoughts..."
                    />
                    <Stack direction="row" spacing={1}>
                      <Button
                        variant="contained"
                        startIcon={<Send />}
                        onClick={handleCreateThread}
                        disabled={!newThreadTitle.trim() || !newThreadContent.trim()}
                      >
                        Post
                      </Button>
                      <Button onClick={() => setShowNewThread(false)}>
                        Cancel
                      </Button>
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            )}

            {threadsLoading ? (
              <CircularProgress />
            ) : (
              <Box>
                {pinnedThreads.length > 0 && (
                  <>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Pinned
                    </Typography>
                    {pinnedThreads.map((thread) => (
                      <ThreadItem
                        key={thread.id}
                        thread={thread}
                        onSelect={setSelectedThread}
                        isSelected={selectedThread?.id === thread.id}
                        currentUserId={user?.id || ''}
                      />
                    ))}
                    {regularThreads.length > 0 && <Divider sx={{ my: 2 }} />}
                  </>
                )}

                {regularThreads.length > 0 ? (
                  regularThreads.map((thread) => (
                    <ThreadItem
                      key={thread.id}
                      thread={thread}
                      onSelect={setSelectedThread}
                      isSelected={selectedThread?.id === thread.id}
                      currentUserId={user?.id || ''}
                    />
                  ))
                ) : (
                  pinnedThreads.length === 0 && (
                    <Typography variant="body2" color="text.secondary" textAlign="center">
                      No discussions yet. Be the first to start one!
                    </Typography>
                  )
                )}
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          {selectedThread ? (
            <Paper sx={{ p: 3 }}>
              <Stack spacing={3}>
                <Box>
                  <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                    {selectedThread.is_pinned && <PushPin color="primary" />}
                    <Typography variant="h5">
                      {selectedThread.title}
                    </Typography>
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Avatar sx={{ width: 32, height: 32 }}>
                      {selectedThread.author_name?.charAt(0) || 'U'}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2">
                        {selectedThread.author_name || 'Unknown'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatDistanceToNow(new Date(selectedThread.created_at), { addSuffix: true })}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>

                <Typography variant="body1">
                  {selectedThread.content}
                </Typography>

                <Divider />

                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">
                    Replies ({replies?.length || 0})
                  </Typography>
                  <IconButton onClick={() => setShowReplies(!showReplies)}>
                    {showReplies ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Stack>

                <Collapse in={showReplies}>
                  <Stack spacing={2}>
                    {repliesLoading ? (
                      <CircularProgress />
                    ) : (
                      replies?.map((reply) => (
                        <ReplyItem
                          key={reply.id}
                          reply={reply}
                          currentUserId={user?.id || ''}
                          isInstructor={isInstructor}
                        />
                      ))
                    )}

                    <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                      <Stack spacing={2}>
                        <TextField
                          fullWidth
                          multiline
                          rows={3}
                          label="Your Reply"
                          value={newReplyContent}
                          onChange={(e) => setNewReplyContent(e.target.value)}
                          placeholder="Add your reply..."
                        />
                        <Button
                          variant="contained"
                          startIcon={<Send />}
                          onClick={handleCreateReply}
                          disabled={!newReplyContent.trim()}
                        >
                          Reply
                        </Button>
                      </Stack>
                    </Paper>
                  </Stack>
                </Collapse>
              </Stack>
            </Paper>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Forum sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Select a thread to view the discussion
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Discussion;