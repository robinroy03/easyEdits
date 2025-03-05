import { useState, useRef } from "react"
import { Upload, Wand2, Play, Volume2, RotateCcw } from "lucide-react"
import "./VideoEditor.css"

export function VideoEditor() {
  const [mediaFiles, setMediaFiles] = useState([])
  const [editedVersions, setEditedVersions] = useState([])
  const [prompt, setPrompt] = useState("")
  const [activeMediaId, setActiveMediaId] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeTab, setActiveTab] = useState("all")

  const fileInputRef = useRef(null)

  const handleUpload = (event) => {
    if (!event.target.files?.length) return

    const files = Array.from(event.target.files)
    const newMediaFiles = files.map((file) => {
      const id = crypto.randomUUID()
      const type = file.type.startsWith("video/") ? "video" : "audio"
      return {
        id,
        file,
        url: URL.createObjectURL(file),
        type,
      }
    })

    setMediaFiles((prev) => [...prev, ...newMediaFiles])

    // Set the first uploaded file as active if none is selected
    if (!activeMediaId && newMediaFiles.length > 0) {
      setActiveMediaId(newMediaFiles[0].id)
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleEdit = () => {
    if (!prompt.trim() || !activeMediaId) return

    setIsProcessing(true)

    // Simulate AI processing delay
    setTimeout(() => {
      const activeMedia = mediaFiles.find((m) => m.id === activeMediaId)
      if (!activeMedia) return

      const newVersion = {
        id: crypto.randomUUID(),
        prompt,
        timestamp: new Date(),
        mediaId: activeMediaId,
        url: activeMedia.url, // In a real app, this would be the new processed video URL
      }

      setEditedVersions((prev) => [...prev, newVersion])
      setPrompt("")
      setIsProcessing(false)
    }, 1500)
  }

  const handleVersionSelect = (version) => {
    setActiveMediaId(version.mediaId)
    // In a real app, you would load the specific version of the edited video
  }

  const activeMedia = activeMediaId ? mediaFiles.find((m) => m.id === activeMediaId) : null

  const filteredVersions = activeMediaId ? editedVersions.filter((v) => v.mediaId === activeMediaId) : []

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
    document.body.classList.toggle("dark-mode")
  }

  const filteredMediaFiles = activeTab === "all" ? mediaFiles : mediaFiles.filter((media) => media.type === activeTab)

  return (
    <div className={`video-editor ${isDarkMode ? "dark-mode" : ""}`}>
      {/* Left Sidebar - Uploaded Media */}
      <div className="sidebar left-sidebar">
        <div className="sidebar-header">
          <h2>Media Library</h2>
          <p className="subtitle">Your uploaded files</p>
        </div>
        <div className="sidebar-content">
          <div className="tabs">
            <button className={`tab ${activeTab === "all" ? "active" : ""}`} onClick={() => setActiveTab("all")}>
              All
            </button>
            <button className={`tab ${activeTab === "video" ? "active" : ""}`} onClick={() => setActiveTab("video")}>
              Video
            </button>
            <button className={`tab ${activeTab === "audio" ? "active" : ""}`} onClick={() => setActiveTab("audio")}>
              Audio
            </button>
          </div>

          <div className="media-list">
            {filteredMediaFiles.length === 0 ? (
              <div className="empty-state">
                <p>No media files uploaded yet</p>
                <p className="subtitle">Upload files to get started</p>
              </div>
            ) : (
              filteredMediaFiles.map((media) => (
                <div
                  key={media.id}
                  onClick={() => setActiveMediaId(media.id)}
                  className={`media-item ${activeMediaId === media.id ? "active" : ""}`}
                >
                  <div className="media-icon">
                    {media.type === "video" ? <Play size={18} /> : <Volume2 size={18} />}
                  </div>
                  <div className="media-details">
                    <p className="media-name">{media.file.name}</p>
                    <div className="media-meta">
                      <span className="badge">{media.type}</span>
                      <span className="file-size">{(media.file.size / (1024 * 1024)).toFixed(2)} MB</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Middle Section - Editor */}
      <div className="editor-main">
        <div className="editor-header">
          <h1>AI Video Editor</h1>
          <button className="button outline" onClick={toggleDarkMode}>
            {isDarkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>

        <div className="editor-content">
          {/* Upload Section */}
          <div className="upload-section">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="video/*,audio/*"
              onChange={handleUpload}
              className="hidden"
              id="media-upload"
            />
            <label htmlFor="media-upload" className="button outline upload-button">
              <Upload size={16} />
              Upload Media
            </label>
          </div>

          {/* Media Preview */}
          {activeMedia ? (
            <div className="media-preview">
              {activeMedia.type === "video" ? (
                <video src={activeMedia.url} controls className="video-player" />
              ) : (
                <div className="audio-player">
                  <Volume2 size={48} />
                  <audio src={activeMedia.url} controls />
                </div>
              )}
            </div>
          ) : (
            <div className="empty-preview">
              <Play size={48} />
              <h3>No media selected</h3>
              <p>Upload or select a file from your library to preview it here</p>
            </div>
          )}

          {/* Prompt Input */}
          <div className="prompt-section">
            <div className="form-group">
              <label htmlFor="prompt">Editing Prompt</label>
              <textarea
                id="prompt"
                placeholder="Describe how you want to edit this video (e.g., 'Remove background noise', 'Add slow motion to the middle section')"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={!activeMedia || isProcessing}
              />
            </div>
            <button
              className="button primary"
              onClick={handleEdit}
              disabled={!activeMedia || !prompt.trim() || isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="spinner"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Wand2 size={16} />
                  Apply AI Edit
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Edited Versions */}
      <div className="sidebar right-sidebar">
        <div className="sidebar-header">
          <h2>Edit History</h2>
          <p className="subtitle">Previous versions</p>
        </div>
        <div className="sidebar-content">
          {!activeMediaId ? (
            <div className="empty-state">
              <p>No media selected</p>
              <p className="subtitle">Select a file to see its edit history</p>
            </div>
          ) : filteredVersions.length === 0 ? (
            <div className="empty-state">
              <p>No edits yet</p>
              <p className="subtitle">Use the prompt to create edited versions</p>
            </div>
          ) : (
            <div className="versions-list">
              {filteredVersions.map((version, index) => (
                <div key={version.id} onClick={() => handleVersionSelect(version)} className="version-item">
                  <div className="version-header">
                    <span className="badge">Version {index + 1}</span>
                    <span className="timestamp">{version.timestamp.toLocaleTimeString()}</span>
                  </div>
                  <p className="version-prompt">{version.prompt}</p>
                  <div className="version-actions">
                    <button className="button small ghost">
                      <RotateCcw size={14} />
                      <span>Restore</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default VideoEditor

