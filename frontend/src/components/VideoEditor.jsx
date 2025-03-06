import { useState, useRef, useEffect } from "react"
import { Upload, Wand2, Play, Volume2, RotateCcw, Sun, Moon } from "lucide-react"
import { FaTrash } from "react-icons/fa"
import "./VideoEditor.css"
import axios from "axios"

export function VideoEditor() {
  const [mediaFiles, setMediaFiles] = useState([])
  const [editedVersions, setEditedVersions] = useState([])
  const [prompt, setPrompt] = useState("")
  const [activeMediaId, setActiveMediaId] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeTab, setActiveTab] = useState("all")
  const [isMentioning, setIsMentioning] = useState(false)
  const [mentionQuery, setMentionQuery] = useState("")
  const [currentVideoUrl, setCurrentVideoUrl] = useState(null)

  const fileInputRef = useRef(null)
  const videoRef = useRef(null)

  // Update current video URL when active media or edited versions change
  useEffect(() => {
    if (!activeMediaId) {
      setCurrentVideoUrl(null)
      return
    }

    // Find the active media
    const activeMedia = mediaFiles.find((m) => m.id === activeMediaId)
    if (!activeMedia) return

    // Check if there are any edited versions for this media
    const versions = editedVersions.filter((v) => v.mediaId === activeMediaId)

    if (versions.length > 0) {
      // Use the most recent edited version
      const latestVersion = versions[versions.length - 1]
      setCurrentVideoUrl(latestVersion.url)
    } else {
      // Use the original media
      setCurrentVideoUrl(activeMedia.url)
    }
  }, [activeMediaId, editedVersions, mediaFiles])

  const handleUpload = async (event) => {
    if (!event.target.files?.length) return

    const files = Array.from(event.target.files)

    const uploadPromises = files.map(async (file) => {
      const formData = new FormData()
      formData.append("file", file)

      try {
        const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })

        if (response.status === 200) {
          const id = crypto.randomUUID()
          const type = file.type.startsWith("video/") ? "video" : "audio"

          return {
            id,
            file,
            url: URL.createObjectURL(file),
            filename: response.data.filename,
            type,
          }
        }
      } catch (error) {
        console.error("Upload failed:", error)
        return null
      }
    })

    const uploadedMediaFiles = (await Promise.all(uploadPromises)).filter(Boolean)

    setMediaFiles((prev) => [...prev, ...uploadedMediaFiles])

    if (!activeMediaId && uploadedMediaFiles.length > 0) {
      setActiveMediaId(uploadedMediaFiles[0].id)
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleEdit = async () => {
    if (!prompt.trim() || !activeMediaId) return

    setIsProcessing(true)

    const activeMedia = mediaFiles.find((m) => m.id === activeMediaId)
    if (!activeMedia) return

    // Determine which version to edit
    const versions = editedVersions.filter((v) => v.mediaId === activeMediaId)
    const currentVersion = versions.length > 0 ? versions[versions.length - 1].versionNumber : activeMedia.filename

    try {
      const response = await axios.post("http://127.0.0.1:8000/query", {
        prompt,
        video_version: currentVersion,
      })

      if (response.status === 200 && response.data[0]) {
        // Create a new URL for the edited video
        const newVersionNumber = response.data[1]
        const editedVideoUrl = `http://127.0.0.1:8000/files/${newVersionNumber}.mp4`

        // Create a new version object
        const newVersion = {
          id: crypto.randomUUID(),
          prompt,
          timestamp: new Date(),
          mediaId: activeMediaId,
          url: editedVideoUrl,
          versionNumber: newVersionNumber.toString(),
        }

        setEditedVersions((prev) => [...prev, newVersion])
        setPrompt("")

        // Force video element to reload with new source
        if (videoRef.current) {
          videoRef.current.load()
        }
      } else {
        console.error("Editing failed:", response.data)
      }
    } catch (error) {
      console.error("Editing failed:", error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleVersionSelect = (version) => {
    // Set the active media ID
    setActiveMediaId(version.mediaId)

    // Update the current video URL to show this specific version
    setCurrentVideoUrl(version.url)

    // Force video element to reload with new source
    if (videoRef.current) {
      videoRef.current.load()
    }
  }

  const handleDelete = async (id) => {
    const media = mediaFiles.find((m) => m.id === id)
    if (!media) return

    try {
      await axios.delete(`http://127.0.0.1:8000/files/${media.filename}`)
      setMediaFiles((prev) => prev.filter((m) => m.id !== id))
      setEditedVersions((prev) => prev.filter((v) => v.mediaId !== id))
      if (activeMediaId === id) {
        setActiveMediaId(null)
        setCurrentVideoUrl(null)
      }
    } catch (error) {
      console.error("Delete failed:", error)
    }
  }

  const activeMedia = activeMediaId ? mediaFiles.find((m) => m.id === activeMediaId) : null

  const filteredVersions = activeMediaId ? editedVersions.filter((v) => v.mediaId === activeMediaId) : []

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
    document.body.classList.toggle("dark-mode")
  }

  const filteredMediaFiles = activeTab === "all" ? mediaFiles : mediaFiles.filter((media) => media.type === activeTab)

  const handlePromptChange = (e) => {
    const value = e.target.value
    setPrompt(value)
    const atIndex = value.lastIndexOf("@")
    if (atIndex >= 0) {
      setIsMentioning(true)
      setMentionQuery(value.substring(atIndex + 1))
    } else {
      setIsMentioning(false)
      setMentionQuery("")
    }
  }

  const handlePromptKeyDown = (e) => {
    if (e.key === "Escape" && isMentioning) {
      setIsMentioning(false)
      setMentionQuery("")
    }
  }

  const handleSelectMention = (filename) => {
    const atIndex = prompt.lastIndexOf("@")
    if (atIndex >= 0) {
      const newPrompt = prompt.substring(0, atIndex) + "@" + filename + " "
      setPrompt(newPrompt)
      setIsMentioning(false)
      setMentionQuery("")
    }
  }

  const mentionSuggestions = mediaFiles.filter((media) =>
    media.file.name.toLowerCase().includes(mentionQuery.toLowerCase()),
  )

  return (
    <div className={`video-editor ${isDarkMode ? "dark-mode" : ""}`}>
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
                  <button className="delete-button" onClick={() => handleDelete(media.id)}>
                    <FaTrash size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="editor-main">
        <div className="editor-header">
          <h1>easyEdits</h1>
          <button className="button outline" onClick={toggleDarkMode}>
            {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>

        <div className="editor-content">
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

          {activeMedia ? (
            <div className="media-preview">
              {activeMedia.type === "video" ? (
                <video
                  ref={videoRef}
                  src={currentVideoUrl || activeMedia.url}
                  controls
                  className="video-player"
                  key={currentVideoUrl} // Force re-render when URL changes
                />
              ) : (
                <div className="audio-player">
                  <Volume2 size={48} />
                  <audio src={currentVideoUrl || activeMedia.url} controls />
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

          <div className="prompt-section" style={{ position: "relative" }}>
            <div className="form-group">
              <label htmlFor="prompt">Editing Prompt</label>
              <textarea
                id="prompt"
                placeholder="Describe how you want to edit this video (e.g., 'Remove background noise', 'Add slow motion to the middle section')"
                value={prompt}
                onChange={handlePromptChange}
                onKeyDown={handlePromptKeyDown}
                disabled={!activeMedia || isProcessing}
              />
              {isMentioning && mentionSuggestions.length > 0 && (
                <div className="mention-dropdown">
                  {mentionSuggestions.map((media) => (
                    <div key={media.id} onClick={() => handleSelectMention(media.file.name)}>
                      {media.file.name}
                    </div>
                  ))}
                </div>
              )}
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