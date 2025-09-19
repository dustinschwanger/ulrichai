import React, { useState, useEffect } from 'react';
import {
  Box,
  Stack,
  Paper,
  Typography,
  Button,
  TextField,
  IconButton,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  NoteAdd,
  Edit,
  Delete,
  MoreVert,
  Save,
  Close,
  FormatBold,
  FormatItalic,
  FormatListBulleted,
  Code,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { config } from '../../../config';
import toast from 'react-hot-toast';

interface Note {
  id: string;
  lessonId: string;
  courseId: string;
  timestamp: string;
  content: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  isEditing?: boolean;
}

interface LessonNotesProps {
  lessonId: string;
  lessonTitle: string;
  courseId: string;
}

const LessonNotes: React.FC<LessonNotesProps> = ({ lessonId, lessonTitle, courseId }) => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteTags, setNewNoteTags] = useState('');
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  // Load notes from backend
  useEffect(() => {
    fetchNotes();
  }, [lessonId]);

  const fetchNotes = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/lessons/${lessonId}/notes`);
      if (response.ok) {
        const data = await response.json();
        // Convert timestamp strings to Date objects
        const notes = data.map((note: any) => ({
          ...note,
          createdAt: new Date(note.createdAt),
          updatedAt: new Date(note.updatedAt)
        }));
        setNotes(notes);
      }
    } catch (error) {
      console.error('Error fetching notes:', error);
      // Fall back to localStorage if API fails
      const savedNotes = localStorage.getItem(`lesson-notes-${lessonId}`);
      if (savedNotes) {
        setNotes(JSON.parse(savedNotes));
      }
    }
  };

  const handleAddNote = async () => {
    if (!newNoteContent.trim()) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/lessons/${lessonId}/notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lessonId,
          courseId,
          content: newNoteContent,
          timestamp: getCurrentVideoTimestamp(),
          tags: newNoteTags.split(',').map(t => t.trim()).filter(t => t),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const note = {
          ...data,
          createdAt: new Date(data.createdAt),
          updatedAt: new Date(data.updatedAt)
        };
        setNotes([note, ...notes]);
        setNewNoteContent('');
        setNewNoteTags('');
        setIsAddingNote(false);
        toast.success('Note saved successfully');

        // Also save to localStorage as backup
        const updatedNotes = [note, ...notes];
        localStorage.setItem(`lesson-notes-${lessonId}`, JSON.stringify(updatedNotes));
      }
    } catch (error) {
      console.error('Error saving note:', error);
      toast.error('Failed to save note');
    }
  };

  const handleUpdateNote = async () => {
    if (!editingNote || !editingNote.content.trim()) return;

    try {
      const response = await fetch(`${config.API_BASE_URL}/notes/${editingNote.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: editingNote.content,
          tags: editingNote.tags,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const updatedNote = {
          ...data,
          createdAt: new Date(data.createdAt),
          updatedAt: new Date(data.updatedAt)
        };
        setNotes(notes.map(n =>
          n.id === editingNote.id ? updatedNote : n
        ));
        setEditingNote(null);
        toast.success('Note updated successfully');

        // Update localStorage
        const updatedNotes = notes.map(n => n.id === editingNote.id ? updatedNote : n);
        localStorage.setItem(`lesson-notes-${lessonId}`, JSON.stringify(updatedNotes));
      }
    } catch (error) {
      console.error('Error updating note:', error);
      toast.error('Failed to update note');
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/notes/${noteId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setNotes(notes.filter(n => n.id !== noteId));
        setAnchorEl(null);
        toast.success('Note deleted successfully');

        // Update localStorage
        const updatedNotes = notes.filter(n => n.id !== noteId);
        localStorage.setItem(`lesson-notes-${lessonId}`, JSON.stringify(updatedNotes));
      }
    } catch (error) {
      console.error('Error deleting note:', error);
      toast.error('Failed to delete note');
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, noteId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedNoteId(noteId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedNoteId(null);
  };

  const getCurrentVideoTimestamp = () => {
    // In production, this would get the actual video timestamp
    const video = document.querySelector('video');
    if (video) {
      const minutes = Math.floor(video.currentTime / 60);
      const seconds = Math.floor(video.currentTime % 60);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    return 'N/A';
  };

  const formatNoteContent = (content: string) => {
    let formatted = content;

    // Bold text
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic text
    formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Bullet points
    formatted = formatted.replace(/^[•\-\*] (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
      return '<ul style="margin: 8px 0; padding-left: 20px;">' + match + '</ul>';
    });

    // Code
    formatted = formatted.replace(/`([^`]+)`/g, '<code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px;">$1</code>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br />');

    return formatted;
  };

  const insertFormatting = (format: string) => {
    const textarea = document.getElementById('note-content') as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = newNoteContent.substring(start, end);
    let formattedText = '';

    switch (format) {
      case 'bold':
        formattedText = `**${selectedText || 'bold text'}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText || 'italic text'}*`;
        break;
      case 'bullet':
        formattedText = `• ${selectedText || 'bullet point'}`;
        break;
      case 'code':
        formattedText = `\`${selectedText || 'code'}\``;
        break;
    }

    const newContent =
      newNoteContent.substring(0, start) +
      formattedText +
      newNoteContent.substring(end);

    setNewNoteContent(newContent);
  };

  // Get all unique tags
  const allTags = Array.from(new Set(notes.flatMap(n => n.tags)));

  // Filter notes based on search and tag
  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.content.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTag = !selectedTag || note.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  return (
    <Box>
      {/* Header with Add Note button */}
      <Stack spacing={2} sx={{ mb: 3 }}>
        <Stack direction="row" spacing={2}>
          <TextField
            fullWidth
            placeholder="Search notes..."
            size="small"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button
            variant="contained"
            startIcon={<NoteAdd />}
            onClick={() => setIsAddingNote(true)}
          >
            Add Note
          </Button>
        </Stack>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="caption" color="text.secondary">
              Filter by tag:
            </Typography>
            <Chip
              label="All"
              size="small"
              onClick={() => setSelectedTag(null)}
              color={!selectedTag ? 'primary' : 'default'}
            />
            {allTags.map(tag => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                onClick={() => setSelectedTag(tag)}
                color={selectedTag === tag ? 'primary' : 'default'}
              />
            ))}
          </Stack>
        )}
      </Stack>

      {/* Notes List */}
      <Stack spacing={2}>
        {filteredNotes.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <NoteAdd sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No notes yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start taking notes to remember key concepts from this lesson!
            </Typography>
          </Paper>
        ) : (
          filteredNotes.map((note) => (
            <Card key={note.id} variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box sx={{ flexGrow: 1 }}>
                    {/* Note Header */}
                    <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1 }}>
                      {note.timestamp !== 'N/A' && (
                        <Chip
                          label={`@ ${note.timestamp}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      <Typography variant="caption" color="text.secondary">
                        {formatDistanceToNow(note.updatedAt, { addSuffix: true })}
                      </Typography>
                    </Stack>

                    {/* Note Content */}
                    {editingNote?.id === note.id ? (
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        value={editingNote.content}
                        onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                        sx={{ mb: 2 }}
                      />
                    ) : (
                      <Typography
                        variant="body2"
                        sx={{ mb: 2 }}
                        dangerouslySetInnerHTML={{ __html: formatNoteContent(note.content) }}
                      />
                    )}

                    {/* Tags */}
                    {note.tags.length > 0 && (
                      <Stack direction="row" spacing={1}>
                        {note.tags.map(tag => (
                          <Chip key={tag} label={tag} size="small" />
                        ))}
                      </Stack>
                    )}
                  </Box>

                  {/* Actions */}
                  <IconButton size="small" onClick={(e) => handleMenuClick(e, note.id)}>
                    <MoreVert />
                  </IconButton>
                </Stack>
              </CardContent>

              {editingNote?.id === note.id && (
                <CardActions>
                  <Button size="small" onClick={() => setEditingNote(null)}>
                    Cancel
                  </Button>
                  <Button size="small" variant="contained" onClick={handleUpdateNote}>
                    Save Changes
                  </Button>
                </CardActions>
              )}
            </Card>
          ))
        )}
      </Stack>

      {/* Note Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem
          onClick={() => {
            const note = notes.find(n => n.id === selectedNoteId);
            if (note) {
              setEditingNote(note);
              handleMenuClose();
            }
          }}
        >
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (selectedNoteId) {
              handleDeleteNote(selectedNoteId);
            }
          }}
        >
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Add Note Dialog */}
      <Dialog
        open={isAddingNote}
        onClose={() => setIsAddingNote(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Add Note
          <IconButton
            sx={{ position: 'absolute', right: 8, top: 8 }}
            onClick={() => setIsAddingNote(false)}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {/* Formatting Toolbar */}
            <Stack direction="row" spacing={1}>
              <IconButton size="small" onClick={() => insertFormatting('bold')}>
                <FormatBold />
              </IconButton>
              <IconButton size="small" onClick={() => insertFormatting('italic')}>
                <FormatItalic />
              </IconButton>
              <IconButton size="small" onClick={() => insertFormatting('bullet')}>
                <FormatListBulleted />
              </IconButton>
              <IconButton size="small" onClick={() => insertFormatting('code')}>
                <Code />
              </IconButton>
            </Stack>

            <TextField
              id="note-content"
              fullWidth
              label="Note"
              placeholder="Type your note here..."
              multiline
              rows={6}
              value={newNoteContent}
              onChange={(e) => setNewNoteContent(e.target.value)}
              required
              helperText="Use **text** for bold, *text* for italic, • for bullets, `text` for code"
            />

            <TextField
              fullWidth
              label="Tags (optional)"
              placeholder="e.g., important, exam, review (comma-separated)"
              size="small"
              value={newNoteTags}
              onChange={(e) => setNewNoteTags(e.target.value)}
            />

            <Typography variant="caption" color="text.secondary">
              Timestamp: {getCurrentVideoTimestamp()}
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddingNote(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleAddNote}
            disabled={!newNoteContent.trim()}
          >
            Save Note
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LessonNotes;