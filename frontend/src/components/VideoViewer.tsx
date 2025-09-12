import React, { useState, useRef, useEffect } from 'react';
import { X, Download, Minimize2, Maximize2, Play, Pause, Volume2, VolumeX } from 'lucide-react';
import ReactPlayer from 'react-player';
import './VideoViewer.css';

interface VideoViewerProps {
  filename: string;
  title: string;
  url?: string;
  startTime?: number; // Start time in seconds
  allowDownload?: boolean;
  onClose: () => void;
}

const VideoViewer: React.FC<VideoViewerProps> = ({
  filename,
  title,
  url,
  startTime = 0,
  allowDownload = false,
  onClose
}) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [muted, setMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [ready, setReady] = useState(false);
  
  const playerRef = useRef<ReactPlayer>(null);

  // Auto-play from startTime when video is ready
  useEffect(() => {
    if (ready && startTime > 0 && playerRef.current) {
      playerRef.current.seekTo(startTime, 'seconds');
      setPlaying(true);
    }
  }, [ready, startTime]);

  const handleProgress = (state: any) => {
    setCurrentTime(state.playedSeconds);
  };

  const handleDuration = (duration: number) => {
    setDuration(duration);
  };

  const handleSeek = (time: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(time, 'seconds');
    }
  };

  const formatTime = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    if (url) {
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const playbackRates = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

  if (!url) {
    return (
      <div className="video-viewer">
        <div className="video-header">
          <h3>{title}</h3>
          <button onClick={onClose} className="close-button">
            <X size={20} />
          </button>
        </div>
        <div className="video-error">
          <p>Video URL not available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`video-viewer ${isMinimized ? 'minimized' : ''}`}>
      <div className="video-header">
        <h3 className="video-title">{title}</h3>
        <div className="video-header-controls">
          {allowDownload && (
            <button onClick={handleDownload} className="header-button" title="Download video">
              <Download size={16} />
            </button>
          )}
          <button 
            onClick={() => setIsMinimized(!isMinimized)} 
            className="header-button"
            title={isMinimized ? "Expand" : "Minimize"}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button onClick={onClose} className="header-button close-button">
            <X size={16} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <div className="video-content">
          <div className="video-player-container">
            <ReactPlayer
              ref={playerRef}
              url={url}
              width="100%"
              height="100%"
              playing={playing}
              volume={volume}
              muted={muted}
              playbackRate={playbackRate}
              onReady={() => setReady(true)}
              onProgress={handleProgress}
              onDuration={handleDuration}
              onPlay={() => setPlaying(true)}
              onPause={() => setPlaying(false)}
              controls={false} // We'll use custom controls
            />
          </div>

          {/* Custom Video Controls */}
          <div className="video-controls">
            <div className="video-controls-row">
              {/* Play/Pause Button */}
              <button 
                onClick={() => setPlaying(!playing)}
                className="control-button play-pause"
              >
                {playing ? <Pause size={16} /> : <Play size={16} />}
              </button>

              {/* Time Display */}
              <span className="time-display">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>

              {/* Progress Bar */}
              <div className="progress-container">
                <input
                  type="range"
                  min={0}
                  max={duration}
                  value={currentTime}
                  onChange={(e) => handleSeek(Number(e.target.value))}
                  className="progress-bar"
                />
              </div>

              {/* Volume Controls */}
              <div className="volume-controls">
                <button 
                  onClick={() => setMuted(!muted)}
                  className="control-button"
                >
                  {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                </button>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={volume}
                  onChange={(e) => setVolume(Number(e.target.value))}
                  className="volume-slider"
                />
              </div>

              {/* Playback Speed */}
              <select 
                value={playbackRate} 
                onChange={(e) => setPlaybackRate(Number(e.target.value))}
                className="playback-rate-select"
              >
                {playbackRates.map(rate => (
                  <option key={rate} value={rate}>{rate}x</option>
                ))}
              </select>
            </div>
          </div>

          {/* Video Info */}
          <div className="video-info">
            <div className="video-filename">{filename}</div>
            {startTime > 0 && (
              <div className="start-time-info">
                Started at: {formatTime(startTime)}
              </div>
            )}
          </div>
        </div>
      )}

      {isMinimized && (
        <div className="video-minimized-content">
          <div className="minimized-info">
            <span className="minimized-title">{title}</span>
            <div className="minimized-controls">
              <button 
                onClick={() => setPlaying(!playing)}
                className="control-button"
              >
                {playing ? <Pause size={14} /> : <Play size={14} />}
              </button>
              <span className="minimized-time">{formatTime(currentTime)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoViewer;