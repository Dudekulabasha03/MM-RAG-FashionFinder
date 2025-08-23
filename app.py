"""
Main application file for the Style Finder Gradio interface.
"""

import gradio as gr
import pandas as pd
import os
from tempfile import NamedTemporaryFile

# Import local modules
from models.image_processor import ImageProcessor
from models.llm_service import OllamaService
from utils.helpers import get_all_items_for_image, format_alternatives_response, process_response
import config

class StyleFinderApp:
    """
    Main application class that orchestrates the Style Finder workflow.
    """
    
    def __init__(self, dataset_path=None):
        """
        Initialize the Style Finder application.
        
        Args:
            dataset_path (str, optional): Path to the dataset file
            
        Raises:
            FileNotFoundError: If the dataset file is not found
            ValueError: If the dataset is empty or invalid
        """
        # Load the dataset or create a dummy one for testing
        if dataset_path and os.path.exists(dataset_path):
            self.data = pd.read_pickle(dataset_path)
            if self.data.empty:
                raise ValueError("The loaded dataset is empty")
        else:
            print(f"Warning: Dataset file not found at {dataset_path}. Creating dummy dataset for testing.")
            # Create a dummy dataset for testing purposes
            import numpy as np
            self.data = pd.DataFrame({
                'Item Name': ['Elegant Blazer', 'Classic Shirt', 'Designer Dress'],
                'Brand': ['Fashion House', 'Style Co.', 'Trendy Brand'],
                'Price': ['$299', '$89', '$199'],
                'Category': ['Blazer', 'Shirt', 'Dress'],
                'Image URL': ['http://example.com/blazer.jpg', 'http://example.com/shirt.jpg', 'http://example.com/dress.jpg'],
                'Embedding': [np.random.random(1000) for _ in range(3)]  # 1000-dimensional vectors
            })
        
        # Initialize components
        self.image_processor = ImageProcessor(
            image_size=config.IMAGE_SIZE,
            norm_mean=config.NORMALIZATION_MEAN,
            norm_std=config.NORMALIZATION_STD
        )
        
        self.llm_service = OllamaService(
            model_name=config.OLLAMA_MODEL_NAME,
            base_url=config.OLLAMA_BASE_URL
        )

    def process_image(self, image):
        """
        Process a user-uploaded image and generate a fashion response.
        
        Args:
            image: File object or file path uploaded through Gradio
                
        Returns:
            str: Formatted response with fashion analysis
        """
        try:
            # Handle file object from Gradio File component
            if hasattr(image, 'name'):  # It's a file object
                image_path = image.name
            elif isinstance(image, str):
                image_path = image
            elif isinstance(image, list) and len(image) > 0:
                # File component returns a list
                if hasattr(image[0], 'name'):
                    image_path = image[0].name
                else:
                    image_path = image[0]
            else:
                return "Error: Invalid image format received"
            
            print(f"Processing image: {image_path}")
            
            # Verify the file exists
            if not os.path.exists(image_path):
                return f"Error: Image file not found at {image_path}"
            
            # Step 1: Encode the image
            user_encoding = self.image_processor.encode_image(image_path, is_url=False)
            if user_encoding['vector'] is None:
                error_msg = user_encoding.get('error', 'Unable to process the image. Please try another image.')
                print(f"Image encoding failed: {error_msg}")
                return f"Error: {error_msg}"
            
            print(f"Image encoded successfully. Vector shape: {user_encoding['vector'].shape}")
            
            # Step 2: Find the closest match
            closest_row, similarity_score = self.image_processor.find_closest_match(user_encoding['vector'], self.data)
            if closest_row is None:
                print("No closest match found in dataset")
                return "Error: Unable to find a match. Please try another image."
            
            print(f"Closest match: {closest_row['Item Name']} with similarity score {similarity_score:.2f}")
            
            # Step 3: Get all related items
            all_items = get_all_items_for_image(closest_row.get('Image URL', ''), self.data)
            if all_items is None or all_items.empty:
                # Create a single-item DataFrame from the closest match for processing
                import pandas as pd
                all_items = pd.DataFrame([{
                    'Item Name': closest_row.get('Item Name', 'Fashion Item'),
                    'Brand': closest_row.get('Brand', 'Unknown'),
                    'Price': closest_row.get('Price', 'N/A'),
                    'Category': closest_row.get('Category', 'Fashion'),
                    'Image URL': closest_row.get('Image URL', '')
                }])
                print("Using single matched item as no related items found.")
            
            # Step 4: Generate fashion response
            bot_response = self.llm_service.generate_fashion_response(
                user_image_base64=user_encoding['base64'],
                matched_row=closest_row,
                all_items=all_items,
                similarity_score=similarity_score,
                threshold=config.SIMILARITY_THRESHOLD
            )
            
            # Clean up temporary file if we created one
            if hasattr(image, 'name') and image.name.startswith('/tmp/'):
                try:
                    os.unlink(image_path)
                except:
                    pass
            
            return process_response(bot_response)
            
        except Exception as e:
            print(f"Error in process_image: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error processing image: {str(e)}"


def create_gradio_interface(app):
    """
    Create and configure the Gradio interface.
    
    Args:
        app (StyleFinderApp): Instance of the StyleFinderApp
        
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    with gr.Blocks(theme=gr.themes.Soft(), title="Fashion Style Analyzer") as demo:
        # Introduction
        gr.Markdown(
            """
            # Men's Fashion Style Analyzer
            
            Upload an image to analyze men's fashion elements and get detailed information about the items.
            This application combines computer vision, vector similarity, and large language models 
            to provide detailed analysis of men's fashion styles, including suits, shirts, accessories, and more.
            """
        )
        
        # Example images section - updated for men's fashion
        gr.Markdown("### Men's Fashion Examples")
        with gr.Row():
            # Display the images directly - show all 6 available images
            gr.Image(value="examples/mens-blazer.jpg", label="Men's Blazer", show_label=True, scale=1)
            gr.Image(value="examples/mens-shirt.jpg", label="Men's Shirt", show_label=True, scale=1)
            gr.Image(value="examples/mens-accessories.jpg", label="Men's Accessories", show_label=True, scale=1)
        
        with gr.Row():
            gr.Image(value="examples/mens-outerwear.jpg", label="Men's Outerwear", show_label=True, scale=1)
            gr.Image(value="examples/mens-formal.jpg", label="Men's Formal Wear", show_label=True, scale=1)
            gr.Image(value="examples/mens-casual.jpg", label="Men's Casual Style", show_label=True, scale=1)
        
        # Example image buttons - updated with men's fashion descriptions
        with gr.Row():
            example1_btn = gr.Button("Use Men's Blazer Example")
            example2_btn = gr.Button("Use Men's Shirt Example")
            example3_btn = gr.Button("Use Men's Accessories Example")
        
        with gr.Row():
            example4_btn = gr.Button("Use Men's Outerwear Example")
            example5_btn = gr.Button("Use Men's Formal Wear Example")
            example6_btn = gr.Button("Use Men's Casual Style Example")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Image input component - fixed to handle all image formats properly
                image_input = gr.File(
                    label="Upload Fashion Image",
                    file_types=["image/*", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
                    file_count="single",
                    type="filepath"
                )
                
                # Submit button
                submit_btn = gr.Button("Analyze Style", variant="primary")
                
                # Status indicator
                status = gr.Markdown("Ready to analyze.")
            
            with gr.Column(scale=2):
                # Output markdown component for displaying analysis results
                output = gr.Markdown(
                    label="Style Analysis Results",
                    height=700
                )
        
        # Event handlers
        # 1. Submit button click with processing indicator
        submit_btn.click(
            fn=lambda: "Analyzing image... This may take a few moments.",
            inputs=None,
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[image_input],
            outputs=output
        ).then(
            fn=lambda: "Analysis complete!",
            inputs=None,
            outputs=status
        )
        
        # 2. Example image buttons - fixed to directly process images
        example1_btn.click(
            fn=lambda: "examples/mens-blazer.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-blazer.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Blazer analysis complete!",
            inputs=None,
            outputs=status
        )
        
        example2_btn.click(
            fn=lambda: "examples/mens-shirt.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-shirt.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Shirt analysis complete!",
            inputs=None,
            outputs=status
        )
        
        example3_btn.click(
            fn=lambda: "examples/mens-accessories.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-accessories.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Accessories analysis complete!",
            inputs=None,
            outputs=status
        )
        
        # New example buttons for 4, 5, and 6 - fixed functionality
        example4_btn.click(
            fn=lambda: "examples/mens-outerwear.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-outerwear.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Outerwear analysis complete!",
            inputs=None,
            outputs=status
        )
        
        example5_btn.click(
            fn=lambda: "examples/mens-formal.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-formal.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Formal Wear analysis complete!",
            inputs=None,
            outputs=status
        )
        
        example6_btn.click(
            fn=lambda: "examples/mens-casual.jpg", 
            inputs=None, 
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[gr.State("examples/mens-casual.jpg")],
            outputs=output
        ).then(
            fn=lambda: "Men's Casual Style analysis complete!",
            inputs=None,
            outputs=status
        )
        
        # Information about the application
        gr.Markdown(
            """
            ### About This Application
            
            This system analyzes fashion images using:
            
            - **Image Encoding**: Converting fashion images into numerical vectors
            - **Similarity Matching**: Finding visually similar items in a database
            - **Advanced AI**: Generating detailed descriptions of fashion elements
            
            The analyzer identifies garments, fabrics, colors, and styling details from images.
            The database includes information on outfits with brand and pricing details.
            """
        )
    
    return demo

if __name__ == "__main__":
    try:
        # Initialize the app with the dataset
        app = StyleFinderApp("swift-style-embeddings.pkl")
        
        # Create the Gradio interface
        demo = create_gradio_interface(app)
        
        # Launch the Gradio interface
        demo.launch(
            server_name="127.0.0.1",  
            server_port=7070,
            share=True  # Set to False if you don't want to create a public link
        )
    except Exception as e:
        print(f"Error starting the application: {str(e)}") 