import { Component, ElementRef, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalysisService, AnalysisResult } from '../../services/analysis.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrls: ['./upload.css']
})
export class UploadComponent implements OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;

  selectedFile: File | null = null;
  isUploading = false;
  message = '';
  result: AnalysisResult | null = null;

  showCamera = false;
  stream: MediaStream | null = null;
  cameraError = '';

  constructor(private analysisService: AnalysisService) { }

  ngOnDestroy(): void {
    this.stopCamera();
  }

  toggleCamera(): void {
    this.showCamera = !this.showCamera;
    if (this.showCamera) {
      this.startCamera();
      this.message = '';
      this.result = null;
      this.selectedFile = null;
    } else {
      this.stopCamera();
    }
  }

  async startCamera(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      if (this.videoElement) {
        this.videoElement.nativeElement.srcObject = this.stream;
      }
      this.cameraError = '';
    } catch (err: any) {
      console.error('Error accessing camera:', err);
      this.cameraError = 'Could not access camera. Please ensure you have granted permission.';
      this.showCamera = false;
    }
  }

  stopCamera(): void {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.nativeElement.srcObject = null;
    }
  }

  capturePhoto(): void {
    if (!this.videoElement || !this.canvasElement) return;

    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const context = canvas.getContext('2d');

    if (context) {
      // Set canvas dimensions to match video stream
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to blob/file
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera-capture.png", { type: "image/png" });
          this.selectedFile = file;
          this.stopCamera();
          this.showCamera = false;
        }
      }, 'image/png');
    }
  }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0] ?? null;
    if (this.selectedFile) {
      this.message = '';
      this.result = null;
    }
  }

  onUpload(): void {
    if (!this.selectedFile) {
      this.message = 'Please select a file or take a photo first.';
      return;
    }

    this.isUploading = true;
    this.message = '';
    this.result = null;

    this.analysisService.uploadImage(this.selectedFile).subscribe({
      next: (response) => {
        this.isUploading = false;
        this.message = 'Analysis Complete!';
        this.result = response;
      },
      error: (err) => {
        this.isUploading = false;
        this.message = 'Upload failed: ' + (err.error?.error || err.message);
      }
    });
  }
}
