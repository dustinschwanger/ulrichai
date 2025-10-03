import React, { useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import {
  Box,
  Paper,
  IconButton,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  TextField,
} from '@mui/material';
import {
  FormatBold,
  FormatItalic,
  FormatUnderlined,
  FormatStrikethrough,
  FormatListBulleted,
  FormatListNumbered,
  FormatAlignLeft,
  FormatAlignCenter,
  FormatAlignRight,
  FormatAlignJustify,
  Link as LinkIcon,
  Image as ImageIcon,
  Code,
  HorizontalRule,
  Undo,
  Redo,
  FormatIndentDecrease,
  FormatIndentIncrease,
  CodeOutlined,
} from '@mui/icons-material';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: number;
}

interface MenuBarProps {
  editor: any;
  showHtml: boolean;
  onToggleHtml: () => void;
}

const MenuBar = ({ editor, showHtml, onToggleHtml }: MenuBarProps) => {
  if (!editor) {
    return null;
  }

  const addLink = () => {
    const url = window.prompt('Enter URL');
    if (url) {
      editor.chain().focus().setLink({ href: url }).run();
    }
  };

  const addImage = () => {
    const url = window.prompt('Enter image URL');
    if (url) {
      editor.chain().focus().setImage({ src: url }).run();
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 1,
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        gap: 1,
        flexWrap: 'wrap',
        alignItems: 'center',
      }}
    >
      {/* Undo/Redo */}
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Tooltip title="Undo">
          <IconButton
            size="small"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
          >
            <Undo fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Redo">
          <IconButton
            size="small"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
          >
            <Redo fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Divider orientation="vertical" flexItem />

      {/* Text Formatting */}
      <ToggleButtonGroup size="small">
        <Tooltip title="Bold">
          <ToggleButton
            value="bold"
            selected={editor.isActive('bold')}
            onClick={() => editor.chain().focus().toggleBold().run()}
          >
            <FormatBold fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Italic">
          <ToggleButton
            value="italic"
            selected={editor.isActive('italic')}
            onClick={() => editor.chain().focus().toggleItalic().run()}
          >
            <FormatItalic fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Underline">
          <ToggleButton
            value="underline"
            selected={editor.isActive('underline')}
            onClick={() => editor.chain().focus().toggleUnderline().run()}
          >
            <FormatUnderlined fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Strikethrough">
          <ToggleButton
            value="strike"
            selected={editor.isActive('strike')}
            onClick={() => editor.chain().focus().toggleStrike().run()}
          >
            <FormatStrikethrough fontSize="small" />
          </ToggleButton>
        </Tooltip>
      </ToggleButtonGroup>

      <Divider orientation="vertical" flexItem />

      {/* Alignment */}
      <ToggleButtonGroup size="small">
        <Tooltip title="Align Left">
          <ToggleButton
            value="left"
            selected={editor.isActive({ textAlign: 'left' })}
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
          >
            <FormatAlignLeft fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Align Center">
          <ToggleButton
            value="center"
            selected={editor.isActive({ textAlign: 'center' })}
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
          >
            <FormatAlignCenter fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Align Right">
          <ToggleButton
            value="right"
            selected={editor.isActive({ textAlign: 'right' })}
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
          >
            <FormatAlignRight fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Justify">
          <ToggleButton
            value="justify"
            selected={editor.isActive({ textAlign: 'justify' })}
            onClick={() => editor.chain().focus().setTextAlign('justify').run()}
          >
            <FormatAlignJustify fontSize="small" />
          </ToggleButton>
        </Tooltip>
      </ToggleButtonGroup>

      <Divider orientation="vertical" flexItem />

      {/* Lists */}
      <ToggleButtonGroup size="small">
        <Tooltip title="Bullet List">
          <ToggleButton
            value="bulletList"
            selected={editor.isActive('bulletList')}
            onClick={() => editor.chain().focus().toggleBulletList().run()}
          >
            <FormatListBulleted fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Numbered List">
          <ToggleButton
            value="orderedList"
            selected={editor.isActive('orderedList')}
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
          >
            <FormatListNumbered fontSize="small" />
          </ToggleButton>
        </Tooltip>
      </ToggleButtonGroup>

      <Divider orientation="vertical" flexItem />

      {/* Indent */}
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Tooltip title="Decrease Indent">
          <IconButton
            size="small"
            onClick={() => editor.chain().focus().liftListItem('listItem').run()}
            disabled={!editor.can().liftListItem('listItem')}
          >
            <FormatIndentDecrease fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Increase Indent">
          <IconButton
            size="small"
            onClick={() => editor.chain().focus().sinkListItem('listItem').run()}
            disabled={!editor.can().sinkListItem('listItem')}
          >
            <FormatIndentIncrease fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Divider orientation="vertical" flexItem />

      {/* Insert */}
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Tooltip title="Add Link">
          <IconButton size="small" onClick={addLink}>
            <LinkIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Add Image">
          <IconButton size="small" onClick={addImage}>
            <ImageIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Code Block">
          <ToggleButton
            value="codeBlock"
            selected={editor.isActive('codeBlock')}
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            size="small"
          >
            <Code fontSize="small" />
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Horizontal Line">
          <IconButton
            size="small"
            onClick={() => editor.chain().focus().setHorizontalRule().run()}
          >
            <HorizontalRule fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Divider orientation="vertical" flexItem />

      {/* HTML Source View Toggle */}
      <Tooltip title={showHtml ? "Visual Editor" : "HTML Source"}>
        <ToggleButton
          value="html"
          selected={showHtml}
          onChange={onToggleHtml}
          size="small"
        >
          <CodeOutlined fontSize="small" />
        </ToggleButton>
      </Tooltip>
    </Paper>
  );
};

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  placeholder = 'Start typing...',
  minHeight = 200,
}) => {
  const [showHtml, setShowHtml] = useState(false);
  const [htmlSource, setHtmlSource] = useState(value || '');

  const editor = useEditor({
    extensions: [
      StarterKit,
      Underline,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          target: '_blank',
        },
      }),
      Image,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
    ],
    content: value || '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      onChange(html);
      setHtmlSource(html);
    },
  });

  // Update editor content when value changes externally
  React.useEffect(() => {
    if (editor && value !== undefined && value !== null) {
      const currentContent = editor.getHTML();
      // Only update if content is actually different to avoid cursor jumping
      if (value !== currentContent) {
        editor.commands.setContent(value || '');
        setHtmlSource(value || '');
      }
    }
  }, [value, editor]);

  const handleToggleHtml = () => {
    if (showHtml) {
      // Switching from HTML to visual - update editor with HTML source
      if (editor) {
        editor.commands.setContent(htmlSource);
        onChange(htmlSource);
      }
    } else {
      // Switching from visual to HTML - sync HTML source
      if (editor) {
        setHtmlSource(editor.getHTML());
      }
    }
    setShowHtml(!showHtml);
  };

  const handleHtmlChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newHtml = e.target.value;
    setHtmlSource(newHtml);
  };

  const handleHtmlBlur = () => {
    // Update editor when leaving HTML view
    if (editor) {
      editor.commands.setContent(htmlSource);
      onChange(htmlSource);
    }
  };

  return (
    <Paper variant="outlined" sx={{ overflow: 'hidden' }}>
      <MenuBar editor={editor} showHtml={showHtml} onToggleHtml={handleToggleHtml} />
      {showHtml ? (
        <TextField
          multiline
          fullWidth
          value={htmlSource}
          onChange={handleHtmlChange}
          onBlur={handleHtmlBlur}
          placeholder="HTML Source"
          sx={{
            '& .MuiInputBase-root': {
              fontFamily: 'monospace',
              fontSize: '14px',
              minHeight,
              maxHeight: 600,
              overflow: 'auto',
              p: 2,
            },
            '& textarea': {
              minHeight: minHeight - 32,
            },
          }}
          InputProps={{
            disableUnderline: true,
          }}
          variant="standard"
        />
      ) : (
        <Box
          sx={{
            minHeight,
            maxHeight: 600,
            overflow: 'auto',
            p: 2,
            '& .ProseMirror': {
            outline: 'none',
            minHeight: minHeight - 32,
            '& p': {
              margin: '0.5em 0',
            },
            '& h1, & h2, & h3, & h4, & h5, & h6': {
              marginTop: '1em',
              marginBottom: '0.5em',
            },
            '& ul, & ol': {
              paddingLeft: '1.5em',
              margin: '0.5em 0',
            },
            '& img': {
              maxWidth: '100%',
              height: 'auto',
            },
            '& pre': {
              backgroundColor: '#f5f5f5',
              padding: '1em',
              borderRadius: '4px',
              overflow: 'auto',
              fontFamily: 'monospace',
            },
            '& code': {
              backgroundColor: '#f5f5f5',
              padding: '0.2em 0.4em',
              borderRadius: '3px',
              fontFamily: 'monospace',
            },
            '& pre code': {
              backgroundColor: 'transparent',
              padding: 0,
            },
            '& hr': {
              margin: '1em 0',
              border: 'none',
              borderTop: '2px solid #ddd',
            },
            '& blockquote': {
              borderLeft: '4px solid #ddd',
              paddingLeft: '1em',
              margin: '1em 0',
              fontStyle: 'italic',
            },
            '& a': {
              color: '#1976d2',
              textDecoration: 'underline',
            },
          },
          '& .ProseMirror p.is-editor-empty:first-child::before': {
            content: `"${placeholder}"`,
            color: '#aaa',
            pointerEvents: 'none',
            height: 0,
            float: 'left',
          },
        }}
        >
          <EditorContent editor={editor} />
        </Box>
      )}
    </Paper>
  );
};

export default RichTextEditor;
