import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalysisService, AnalysisResult } from '../../services/analysis.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrls: ['./upload.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  isUploading = false;
  message = '';
  result: AnalysisResult | null = null;

  constructor(private analysisService: AnalysisService) { }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0] ?? null;
  }

  onUpload(): void {
    if (!this.selectedFile) {
      this.message = 'Please select a file first.';
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
