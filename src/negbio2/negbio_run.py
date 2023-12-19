"""
Split text into sentences, Parse sentences, Convert from parse tree to universal dependencies, Detect negation and uncertainty

Usage:
    negbio_run [options] 

Options:
    --newline_is_sentence_break     Whether to treat newlines as sentence breaks. True means that
                                    a newline is always a sentence break. False means to ignore
                                    newlines for the purpose of sentence splitting. This is
                                    appropriate for continuous text, when just the non-whitespace
                                    characters should be used to determine sentence breaks.
                                    [default=False]
    --suffix=<suffix>               Append an additional SUFFIX to file names.
                                    [default: .neg2.xml]
    --output=<directory>            Specify the output directory.
    --verbose                       Print more information about progress.
    --overwrite                     Overwrite the output file.
    --workers=<n>                   Number of threads [default: 1]
    --files_per_worker=<n>          Number of input files per worker [default: 8]

    --neg-patterns=FILE                         Negation rules [default: patterns/neg_patterns2.yml]
    --pre-negation-uncertainty-patterns=FILE    Pre negation uncertainty rules
                                                [default: patterns/chexpert_pre_negation_uncertainty.yml]
    --post-negation-uncertainty-patterns=FILE   Post negation uncertainty rules
                                                [default: patterns/post_negation_uncertainty.yml]
    --neg-regex-patterns=FILE                   Regex Negation rules [default: patterns/neg_regex_patterns.yml]
    --uncertainty-regex-patterns=FILE           Regex uncertainty rules [default: patterns/uncertainty_regex_patterns.yml]

"""


from negbio2.negbio.pipeline2.pipeline import NegBioPipeline
from negbio2.negbio.pipeline2.ssplit import NegBioSSplitter
from negbio2.negbio.pipeline2.parse import NegBioParser
from negbio2.negbio.pipeline2.ptb2ud import NegBioPtb2DepConverter
from negbio2.negbio.pipeline2.negdetect2 import NegBioNegDetector2, Detector2
from negbio2.negbio.pipeline2.cleanup import CleanUp
from negbio2.negbio.cli_utils import parse_args, calls_asynchronously


def negbio_load():

    argv = {'--files_per_worker': '8',
            '--neg-patterns': './negbio2/patterns/neg_patterns2.yml',
            '--neg-regex-patterns': './negbio2/patterns/neg_regex_patterns.yml',
            '--newline_is_sentence_break': False,
            '--output': '',
            '--overwrite': False,
            '--post-negation-uncertainty-patterns': './negbio2/patterns/post_negation_uncertainty.yml',
            '--pre-negation-uncertainty-patterns': './negbio2/patterns/chexpert_pre_negation_uncertainty.yml',
            '--suffix': '.neg2.xml',
            '--uncertainty-regex-patterns': './negbio2/patterns/uncertainty_regex_patterns.yml',
            '--verbose': False,
            '--workers': '1',
            '<file>': ['']}
        

    # print(argv)
    splitter = NegBioSSplitter(newline=argv['--newline_is_sentence_break'])
    parser = NegBioParser(model_dir='./negbio2/parse_model') #argv['--model']
    converter = NegBioPtb2DepConverter(universal=True)
    
    neg_detector = NegBioNegDetector2(
        Detector2(argv['--pre-negation-uncertainty-patterns'],
                    argv['--neg-patterns'],
                    argv['--post-negation-uncertainty-patterns'],
                    argv['--neg-regex-patterns'],
                    argv['--uncertainty-regex-patterns']))
    cleanup = CleanUp()
    pipeline = NegBioPipeline(pipeline=[('NegBioSSplitter', splitter), ('NegBioParser', parser), ('NegBioPtb2DepConverter', converter), ('NegBioNegDetector', neg_detector), ('CleanUp', cleanup)])

    return pipeline, argv

def negbio_main(pipeline, argv,infile, outpath):
    '''
    argv = {'--files_per_worker': '8',
            '--neg-patterns': './negbio2/patterns/neg_patterns2.yml',
            '--neg-regex-patterns': './negbio2/patterns/neg_regex_patterns.yml',
            '--newline_is_sentence_break': False,
            '--output': './test_out/',
            '--overwrite': False,
            '--post-negation-uncertainty-patterns': './negbio2/patterns/post_negation_uncertainty.yml',
            '--pre-negation-uncertainty-patterns': './negbio2/patterns/chexpert_pre_negation_uncertainty.yml',
            '--suffix': '.neg2.xml',
            '--uncertainty-regex-patterns': './negbio2/patterns/uncertainty_regex_patterns.yml',
            '--verbose': False,
            '--workers': '1',
            '<file>': ['/home/Users/luol/PhenoTagger_v1.2_github/example/output_test/ex.xml']}
        
    argv['--output'] = outpath
    argv['<file>'] = [infile]
    # print(argv)
    splitter = NegBioSSplitter(newline=argv['--newline_is_sentence_break'])
    parser = NegBioParser(model_dir='./negbio2/parse_model') #argv['--model']
    converter = NegBioPtb2DepConverter(universal=True)
    
    neg_detector = NegBioNegDetector2(
        Detector2(argv['--pre-negation-uncertainty-patterns'],
                    argv['--neg-patterns'],
                    argv['--post-negation-uncertainty-patterns'],
                    argv['--neg-regex-patterns'],
                    argv['--uncertainty-regex-patterns']))
    cleanup = CleanUp()
    pipeline = NegBioPipeline(pipeline=[('NegBioSSplitter', splitter), ('NegBioParser', parser), ('NegBioPtb2DepConverter', converter), ('NegBioNegDetector', neg_detector), ('CleanUp', cleanup)])
    '''
    argv['--output'] = outpath
    argv['<file>'] = [infile]
    pipeline.scan(source=argv['<file>'], directory=argv['--output'], suffix=argv['--suffix'],
                    overwrite=argv['--overwrite'])


if __name__ == '__main__':
    argv = parse_args(__doc__)
    workers = int(argv['--workers'])
    if workers == 1:
        
        argv['--output'] = './test_out/'
        argv['<file>'] = ['/home/Users/luol/PhenoTagger_v1.2_github/example/output_test/ex.xml']
        print(argv)
        splitter = NegBioSSplitter(newline=argv['--newline_is_sentence_break'])
        parser = NegBioParser(model_dir='./parse_model') #argv['--model']
        converter = NegBioPtb2DepConverter(universal=True)
        
        neg_detector = NegBioNegDetector2(
            Detector2(argv['--pre-negation-uncertainty-patterns'],
                      argv['--neg-patterns'],
                      argv['--post-negation-uncertainty-patterns'],
                      argv['--neg-regex-patterns'],
                      argv['--uncertainty-regex-patterns']))
        cleanup = CleanUp()
        pipeline = NegBioPipeline(pipeline=[('NegBioSSplitter', splitter), ('NegBioParser', parser), ('NegBioPtb2DepConverter', converter), ('NegBioNegDetector', neg_detector), ('CleanUp', cleanup)])

        pipeline.scan(source=argv['<file>'], directory=argv['--output'], suffix=argv['--suffix'],
                      overwrite=argv['--overwrite'])

        

        
    else:
        calls_asynchronously(argv, 'python -m negbio.negbio_ssplit')
